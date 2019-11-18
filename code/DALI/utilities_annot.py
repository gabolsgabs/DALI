""" Utilities functions for dealing with the dali dataset.

It includes all the needed functions for reading files and the helpers for
transforming the annotation information.

GABRIEL MESEGUER-BROCAL 2018
"""
import copy
import numpy as np
from .features_list import FREQS


# -------------- CHANING ANNOTATIONS --------------
def freq2midi(freq, ref=69):
    return np.round(12 * np.log2(freq/440.) + ref).astype(int)


def midi2freq(midi):
    return np.around((np.power(2, (midi-69)/12) * 440), decimals=2)


def change_note(freq, transposition):
    midi = freq2midi(freq) + transposition
    new_freq = midi2freq(midi)
    return new_freq


def change_note_tuple(freq, transposition):
    return tuple(change_note(f, transposition) for f in freq)


def compute_new_time(annot, old_fr, new_fr, new_offset=None):
    n_time = np.array([e['time'] for e in annot])
    if new_offset is None:
        new_offset = n_time[0, 0]
    if new_fr != old_fr:
        n_time = (n_time*old_fr)/new_fr
    n_time += new_offset - n_time[0, 0]
    for i, e in enumerate(annot):
        e['time'] = tuple(n_time[i])
    return annot


def find_nearest(array, value):
    import numpy as np
    vocal_range = [FREQS[0], FREQS[-1]]
    while value < vocal_range[0]:
        value *= 2.
    while value > vocal_range[1]:
        value /= 2.
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx


def compute_new_notes(lst, bins_trans, freqs=FREQS):
    for e in lst:
        _, idx = find_nearest(freqs, e['freq'][0])
        new_freq = freqs[idx+bins_trans]
        e['freq'] = (new_freq, new_freq)
    return lst


# -------------- TRANSFORMING THE INFO IN THE ANNOTATIONS --------------


def roll(lower, upper):
    """It merges an horizontal level with its upper. For example melody with
    words or lines with paragraphs
    """
    tmp = copy.deepcopy(lower)
    for info in tmp:
        i = info['index']
        if not isinstance(upper[i]['text'], list):
            upper[i]['text'] = []
        info.pop('index', None)
        upper[i]['text'].append(info)
    return upper


def get_text(text, output=[], m=False):
    """Recursive function for having the needed text for the unroll function.
    """
    f = lambda x: isinstance(x, unicode) or isinstance(x, str)
    try:
        f('whatever')
    except Exception:
        f = lambda x: isinstance(x, str)
    if isinstance(text, list):
        tmp = [get_text(i['text'], output) for i in text]
        if f(tmp[0]):
            output.append(''.join(tmp))
    elif f(text):
        output = text
    return output


def unroll(annot, output=[], depth=0, index=0, b=False):
    """Recursive function that transforms an annotation vector in the format
    vertical format into a horizontal vector:
        - annot (list): annotations vector in vertical formart.
        - output (list): internally used in the recursion, final output.
        - depth (int): depth that the recursion is going to be.
            Example:
            1 - input list of paragraph (annot)
                depth = 0 -> output = horizontal level for paragraphs,
                depth = 1 -> output = lines, depth = 2 -> output = words
                depth = 3 -> output = melody
            2 - input a list of lines (annot[paragraph_i]['text'][line_i])
                depth = 0 -> output = lines, depth = 1 -> words,
                depth = 2 -> melody,
                depth = 3 -> ERROR: not controlled behaviour
        - b (bool) = control if the horizontal level is going to have index
            or not. The paragraph level does not need it.
    """
    if depth == 0:
        """Bottom level to be merged"""
        for i in annot:
            text = get_text(i['text'], output=[])
            if isinstance(text, list):
                text = " ".join(text)
            output.append({'time': i['time'], 'freq': i['freq'], 'text': text})
            if b:
                output[-1]['index'] = index
        index += 1
    else:
        """Go deeper"""
        depth -= 1
        b = True
        for l in annot:
            output, index = unroll(l['text'], output, depth, index, b)
    return output, index


def sample(annot, time_r):
    """Transform the normal time into a discrete value with respect time_r.
    """
    output = copy.deepcopy(annot)
    for a in output:
        a['time'] = (np.round(a['time'][0]/time_r).astype(int),
                     np.round(a['time'][1]/time_r).astype(int))
    return output
