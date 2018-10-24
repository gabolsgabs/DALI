""" ANNOTATIONS class and some extra useful functions: annot2vector,
annot2frames, unroll and roll.

These extra functions transformation the annots a song into different
representations. They are disconnected to the class because they can be
applyied to a subsection i.e. for transforming only one indivual level
to a vector representation.


GABRIEL MESEGUER-BROCAL 2018
"""
import copy
import numpy as np
import DALI.utilities as ut


def unroll(annot):
    """Unrolls the hierarchical information into paragraphs, lines, words
    keeping the relations with the key 'index.'
    """
    tmp = copy.deepcopy(annot['hierarchical'])
    p, _ = ut.unroll(tmp, depth=0, output=[])
    l, _ = ut.unroll(tmp, depth=1, output=[])
    w, _ = ut.unroll(tmp, depth=2, output=[])
    m, _ = ut.unroll(tmp, depth=3, output=[])
    return {'paragraphs': p, 'lines': l, 'words': w, 'notes': m}


def roll(annot):
    """Rolls the individual info into a hierarchical level.

    Output example: [paragraph]['text'][line]['text'][word]['text'][notes]'
    """
    tmp = copy.deepcopy(annot)
    output = ut.roll(tmp['notes'], tmp['words'])
    output = ut.roll(output, tmp['lines'])
    output = ut.roll(output, tmp['paragraphs'])
    return {'hierarchical': output}


def annot2frames(annot, time_r, type='horizontal', depth=3):
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
        type : str
            annotation format: horizontal or vertical.
        depth : int
            depth of the horizontal level.
    """
    output = []
    tmp = copy.deepcopy(annot)
    try:
        if type == 'horizontal':
            output = ut.sample(tmp, time_r)
        elif type == 'vertical':
            vertical = [ut.sample(ut.unroll(tmp, [], depth=depth)[0], time_r)
                        for i in range(depth+1)][::-1]
            for i in range(len(vertical[:-1])):
                if i == 0:
                    output = roll(vertical[i], vertical[i+1])
                else:
                    output = roll(output, vertical[i+1])
    except Exception as e:
        print('ERROR: unknow type of annotations')
    return output


def annot2vector(annot, duration, time_r, type='voice'):
    """Transforms the annotations into frame vector wrt a time resolution.

    Parameters
    ----------
        annot : list
            annotations only horizontal level
            (for example: annotations['annot']['lines'])
        time_r : float
            time resolution for discriticing the time.
        dur : float
            duration of the vector (for adding zeros).
        type : str
            'voice': each frame has a value 1 or 0 for voice or not voice.
            'notes': each frame has the freq value of the main vocal melody.
    """
    singal = np.zeros(int(duration / time_r))
    for note in annot:
        b, e = note['time']
        b = np.round(b/time_r).astype(int)
        e = np.round(e/time_r).astype(int)
        if type == 'voice':
            singal[b:e+1] = 1
        if type == 'melody':
            singal[b:e+1] = np.mean(note['freq'])
    return singal


def annot2vector_chopping(annot, dur, sr, win_bin, hop_bin, type='voice'):
    """
    Transforms the annotations into a frame vector by:

        1 - creating a vector singal for a give sample rate
        2 - chopping it using the given hop and wind size.

    Parameters
    ----------
        annot : list
            annotations only horizontal level
            (for example: annotations['annot']['lines'])
        dur : float
            duration of the vector (for adding zeros).
        sr : float
            sample rate for discriticing annots.
        win_bin : int
            window size in bins for sampling the vector.
        hop_bin: int
            hope size in bins for sampling the vector.
        type :str
            'voice': each frame has a value 1 or 0 for voice or not voice.
            'notes': each frame has the freq value of the main vocal melody.
    """
    output = []
    try:
        singal = annot2vector(annot, dur, sr, type)
        win = np.hanning(win_bin)
        win_sum = np.sum(win)
        v = hop_bin*np.arange(int((len(singal)-win_bin)/hop_bin+1))
        output = np.array([np.sum(win[::-1]*singal[i:i+win_bin])/win_sum
                           for i in v]).T
    except Exception as e:
        print('ERROR: unknow type of annotations')
    return output


class Annotations(object):
    """Basic class that store annotations and its information.

    It contains some method for transformin the annot representation.
    """

    def __init__(self, i):
        self.info = {'id': i, 'artist': 'None', 'title': 'None',
                     'audio': {'url': 'None', 'working': False, 'path': 'None'},
                     'metadata': {}, 'scores': {'NCC': 0.0, 'manual': 0.0},
                     'dataset_version': 0.0, 'ground-truth': 'None'}
        self.annotations = {'type': 'None', 'annot': {},
                            'annot_param': {'fr': 0.0, 'offset': 0.0}}
        self.errors = None
        return

    def read_json(self, fname):
        """Read the annots from a json file."""
        data = ut.read_json(fname)
        if(ut.check_structure(self.info, data['info']) and
           ut.check_structure(self.annotations, data['annotations'])):
            self.info = data['info']
            self.annotations = data['annotations']
        else:
            print('ERROR: wrong format')
        return

    def write_json(self, pth, name):
        """Writes the annots into a json file."""
        data = {'info': self.info, 'annotations': self.annotations}
        ut.write_in_json(pth, name, data)
        return

    def horizontal2vertical(self):
        """Converts horizontal annotations (indivual levels) into a vertical
        representation (hierarchical)."""
        try:
            if self.annotations['type'] == 'horizontal':
                self.annotations['annot'] = roll(self.annotations['annot'])
                self.annotations['type'] = 'vertical'
            else:
                print('Annot are already in a horizontal format')
        except Exception as e:
            print('ERROR: unknow type of annotations')
        return

    def vertical2horizontal(self):
        """Converts vertical representation (hierarchical) into a  horizontal
        annotations (indivual levels)."""
        try:
            if self.annotations['type'] == 'vertical':
                self.annotations['annot'] = unroll(self.annotations['annot'])
                self.annotations['type'] = 'horizontal'
            else:
                print('Annot are already in a vertical format')
        except Exception as e:
            print('ERROR: unknow type of annotations')
        return

    def is_horizontal(self):
        output = False
        if self.annotations['type'] == 'horizontal':
            output = True
        return output

    def is_vertical(self):
        output = False
        if self.annotations['type'] == 'vertical':
            output = True
        return output
