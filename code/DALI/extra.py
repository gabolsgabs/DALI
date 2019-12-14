""" Extra function: annot2vector, annot2frames, unroll and roll.

Transformating the annots a song into different representations.
They are disconnected to the class because they can be
applyied to a subsection i.e. for transforming only one indivual level
to a vector representation.


GABRIEL MESEGUER-BROCAL 2018
"""
import copy
import numpy as np
from .download import audio_from_url
from . import utilities_annot as uta
from .utilities_annot import find_nearest
from .features_list import FREQS, PHONEMES, CHAR, PHONEMES_TYPE, PHONEMES_DICT


def unroll(annot):
    """Unrolls the hierarchical information into paragraphs, lines, words
    keeping the relations with the key 'index.'
    """
    tmp = copy.deepcopy(annot['hierarchical'])
    p, _ = uta.unroll(tmp, depth=0, output=[])
    l, _ = uta.unroll(tmp, depth=1, output=[])
    w, _ = uta.unroll(tmp, depth=2, output=[])
    m, _ = uta.unroll(tmp, depth=3, output=[])
    return {'paragraphs': p, 'lines': l, 'words': w, 'notes': m}


def roll(annot):
    """Rolls the individual info into a hierarchical level.

    Output example: [paragraph]['text'][line]['text'][word]['text'][notes]'
    """
    tmp = copy.deepcopy(annot)
    output = uta.roll(tmp['notes'], tmp['words'])
    # if 'phonemes' in tmp:
    #     output = uta.roll(output, tmp['phonemes'])
    output = uta.roll(output, tmp['lines'])
    output = uta.roll(output, tmp['paragraphs'])
    return {'hierarchical': output}


def annot2frames(annot, time_r, t='horizontal', depth=3):
    """Transforms annot time into a discrete formart wrt a time_resolution.

    This function can be use with the whole annotation or with a subset.
    For example, it can be called with a particular paragraph in the horizontal
    format [annot[paragraph_i]] or line [annot[paragraph_i]['text'][line_i]].

    Parameters
    ----------
        annot : list
            annotations vector (annotations['annot']) in any the formats.
        time_r : float
            time resolution for discriticing the time.
        t : str
            annotation type: horizontal or vertical.
        depth : int
            depth of the horizontal level.
    """
    output = []
    tmp = copy.deepcopy(annot)
    try:
        if t == 'horizontal':
            output = uta.sample(tmp, time_r)
        elif t == 'vertical':
            vertical = [uta.sample(uta.unroll(tmp, [], depth=depth)[0], time_r)
                        for i in range(depth+1)][::-1]
            for i in range(len(vertical[:-1])):
                if i == 0:
                    output = roll(vertical[i], vertical[i+1])
                else:
                    output = roll(output, vertical[i+1])
    except Exception:
        print('ERROR: unknow type of annotations')
    return output


def annot2vector(annot, duration, time_r, t='voice'):
    """Transforms the annotations into frame vector wrt a time resolution.

    Parameters
    ----------
        annot : list
            annotations only horizontal level
            (for example: annotations['annot']['lines'])
        duration : float
            duration of the vector (for adding zeros).
        time_r : float
            time resolution for discriticing the time.
        t : str
            'voice': each frame has a value 1 or 0 for voice or not voice.
            'notes': each frame has the freq value of the main vocal melody.
    """
    signal = np.zeros(int(duration / time_r))
    for info in annot:
        b, e = info['time']
        b = np.round(b/time_r).astype(int)
        e = np.round(e/time_r).astype(int)
        if t == 'voice':
            signal[b:e+1] = 1
        if t == 'melody':
            signal[b:e+1] = np.mean(info['freq'])
    return signal


def annot2matrix(annot, time_r, dur, t):
    """Transforms the annotations into frame vector wrt a time resolution.

    Parameters
    ----------
        annot : list
            annotations only horizontal level
            (for example: annotations['annot']['notes'])
        time_r : float
            time resolution for discriticing the time.
        t : str
            'notes':
            'char':
            'phoneme':
            'phoneme_type':
    """
    if t == 'chars':
        features = CHAR
    if t == 'phonemes':
        features = PHONEMES
    if t == 'phoneme_types':
        features = PHONEMES_TYPE
    if t == 'notes':
        features = FREQS
    signal = np.zeros((len(features)+1, np.round(dur/time_r).astype(int)+1))
    signal[-1, :] = 1    # adding a blank value
    for info in annot:
        b, e = info["time"]
        b = np.round(b / time_r).astype(int)
        e = np.round(e / time_r).astype(int)
        if t == "notes":
            value, bin = find_nearest(features, info['freq'][0])
            # earsing the blank value
            signal[:, b:e + 1] = 0
            signal[bin, b:e + 1] = 1
        if t == 'chars' or t == 'phonemes' or t == 'phoneme_types':
            if t == 'phoneme_types':
                info['text'] = [PHONEMES_DICT[i] for i in info['text']]
            # earsing the blank value
            signal[:, b:e + 1] = 0
            for dx, i in enumerate(info['text']):
                if i in features:
                    signal[features.index(i), b:e + 1] = dx+1
    return signal


def annot2vector_chopping(annot, dur, time_r, win_bin, hop_bin, t='voice'):
    """
    Transforms the annotations into a frame vector by:

        1 - creating a vector signal for a give sample rate
        2 - chopping it using the given hop and wind size.

    Parameters
    ----------
        annot : list
            annotations only horizontal level
            (for example: annotations['annot']['lines'])
        dur : float
            duration of the vector (for adding zeros).
        time_r : float
            sample rate for discriticing annots.
        win_bin : int
            window size in bins for sampling the vector.
        hop_bin: int
            hope size in bins for sampling the vector.
        t :str
            'voice': each frame has a value 1 or 0 for voice or not voice.
            'notes': each frame has the freq value of the main vocal melody.
    """
    output = []
    try:
        signal = annot2vector(annot, dur, time_r, t)
        win = np.hanning(win_bin)
        win_sum = np.sum(win)
        v = hop_bin*np.arange(int((len(signal)-win_bin)/hop_bin+1))
        output = np.array([np.sum(win[::-1]*signal[i:i+win_bin])/win_sum
                           for i in v]).T
    except Exception:
        print('ERROR: unknow type of annotations')
    return output


def get_audio(dali_info, path_output, skip=[], keep=[]):
    """Get the audio for the dali dataset.

    It can download the whole dataset or only a subset of the dataset
    by providing either the ids to skip or the ids that to load.

    Parameters
    ----------
        dali_info : list
            where elements are ['DALI_ID', 'NAME', 'YOUTUBE', 'WORKING']
        path_output : str
            full path for storing the audio
        skip : list
            list with the ids to be skipped.
        keep : list
            list with the ids to be keeped.
    """
    errors = []
    if len(keep) > 0:
        for i in dali_info[1:]:
            if i[0] in keep:
                _ = audio_from_url(i[-2], i[0], path_output, errors)
    else:
        for i in dali_info[1:]:
            if i[0] not in skip:
                _ = audio_from_url(i[-2], i[0], path_output, errors)
    return errors
