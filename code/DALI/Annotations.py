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
import utilities as ut


def unroll(annot):
    """ Unroll the hierarchical information (paragraphs[lines[words[notes]]])
    into paragraphs, lines, words keeping the relations with the key 'index.'
    """
    tmp = copy.deepcopy(annot['hierarchical'])
    p, _ = ut.unroll(tmp, depth=0, output=[])
    l, _ = ut.unroll(tmp, depth=1, output=[])
    w, _ = ut.unroll(tmp, depth=2, output=[])
    m, _ = ut.unroll(tmp, depth=3, output=[])
    return {'paragraphs': p, 'lines': l, 'words': w, 'notes': m}


def roll(annot):
    """ Roll the individual information into a hierarchical level
    ([paragraph]['text'][line]['text'][word]['text'][notes]).'
    """
    tmp = copy.deepcopy(annot)
    output = ut.roll(tmp['notes'], tmp['words'])
    output = ut.roll(output, tmp['lines'])
    output = ut.roll(output, tmp['paragraphs'])
    return {'hierarchical': output}


def annot2frames(annot, time_r, type='horizontal', depth=3):
    """Transform the normal time of annotations into a discrete formar
    with respect to a time_resolution:
        - annot (list): annotations vector (annotations['annot'])
            in any of the two formats.
        - time_r (float): time resolution for discriticing the time.
        - type (str): annotation format: horizontal or vertical.
        - depth (int): depth of the horizontal level.
    This function can be use with the whole annotation or with a subset.
    For example, it can be called with a particular paragraph in the horizontal
    format [annot[paragraph_i]] or line [annot[paragraph_i]['text'][line_i]].
    """
    output = []
    try:
        if type == 'horizontal':
            output = ut.sample(annot, time_r)
        elif type == 'vertical':
            vertical = [ut.sample(ut.unroll(annot, [], depth=depth)[0], time_r)
                        for i in range(depth+1)][::-1]
            for i in range(len(vertical[:-1])):
                if i == 0:
                    output = roll(vertical[i], vertical[i+1])
                else:
                    output = roll(output, vertical[i+1])
    except Exception as e:
        print('ERROR: unknow type of annotations')
    return output


def annot2vector(annot, time_r, dur, win_bin, hop_bin, type='voice'):
    """Transform a normal annotations into frame vector:
        - annot (list): annotations only horizontal level
            (for example: annotations['annot']['lines'])
        - time_r (float): time resolution for discriticing the time.
        - dur (float): duration of the vector (for adding zeros).
        - win_bin (int): window size in bins for sampling the vector.
        - hop_bin (int): hope size in bins for sampling the vector.
    """
    output = []
    try:
        singal = np.zeros(int(dur / time_r))
        for note in annot:
            b, e = note['time']
            b = np.round(b/time_r).astype(int)
            e = np.round(e/time_r).astype(int)
            if type == 'voice':
                singal[b:e+1] = 1
            if type == 'notes':
                singal[b:e+1] = np.mean(note['freq'])
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
    It contains some method for transformin the annot representation."""

    def __init__(self, i):
        self.info = {'id': i, 'artist': None, 'title': None, 'metadata': None,
                     'audio': {'url': None, 'working': None, 'path': None},
                     'scores': {'NCC': None, 'manual': None},
                     'dataset_version': None, 'ground-truth': None}
        self.annotations = {'type': None, 'annot': None,
                            'annot_param': {'fr': None, 'offset': None}}
        self.errors = None
        return

    def read_json(self, fname):
        """Read the annots from a json file."""
        data = ut.read_json(fname)
        if (ut.check_structure(self.info, data['info']) and
           ut.check_structure(self.annotations, data['annotations'])):
            self.info = data['info']
            self.annotations = data['annotations']
        else:
            print('ERROR: wrong format')
        return

    def write_json(self, pth, name):
        """Write the annots into a json file."""
        data = {'info': self.info, 'annotations': self.annotations}
        ut.write_in_json(pth, name, data)
        return

    def horizontal2vertical(self):
        """Convert horizontal annotations (indivual levels) into a vertical
        representation (hierarchical)."""
        try:
            if self.annotations['type'] == 'horizontal':
                self.annotations['type'] = 'vertical'
                self.annotations['annot'] = roll(self.annotations['annot'])
            else:
                print('Annot are already in a horizontal format')
        except Exception as e:
            print('ERROR: unknow type of annotations')
        return

    def vertical2horizontal(self):
        """Convert vertical representation (hierarchical) into a  horizontal
        annotations (indivual levels)."""
        try:
            if self.annotations['type'] == 'vertical':
                self.annotations['type'] = 'horizontal'
                self.annotations['annot'] = unroll(self.annotations['annot'])
            else:
                print('Annot are already in a vertical format')
        except Exception as e:
            print('ERROR: unknow type of annotations')
        return
