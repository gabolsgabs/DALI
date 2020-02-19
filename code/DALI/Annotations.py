""" ANNOTATIONS class.

GABRIEL MESEGUER-BROCAL 2018
"""
import copy
from .extra import (
    unroll, roll, annot2vector, annot2vector_chopping, annot2matrix,
    annot2pandas
)
from .align import (align_brute_force, align_offset)
from .download import audio_from_url
from . import utilities as ut
from . import utilities_annot as uta
from .utilities_audio import end_song
from .features_list import FREQS


class Annotations(object):
    """Basic class that store annotations and its information.

    It contains some method for transformin the annot representation.
    """

    def __init__(self, i=u'None'):
        self.info = {'id': i, 'artist': u'None', 'title': u'None',
                     'audio': {'url': u'None', 'working': False,
                               'path': u'None'},
                     'metadata': {}, 'scores': {'NCC': 0.0, 'manual': 0.0},
                     'dataset_version': 0.0, 'ground-truth': False}
        self.annotations = {'type': u'None', 'annot': {},
                            'annot_param': {'fr': 0.0, 'offset': 0.0}}
        self.errors = None
        return

    def read_json(self, fname):
        """Read the annots from a json file."""
        data = ut.read_json(fname)
        if(ut.check_structure(self.info, data['info'])
           and ut.check_structure(self.annotations, data['annotations'])):
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
        except Exception:
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
        except Exception:
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

    def realign(self, path_audio, pred, p='both', g='notes'):
        """Align the annotations to a new audio track.
        Parameters
        ----------
        path_audio : text
            New audio to which the annotation will be globally adapted.
        pred : np.array
            a singing voice probability vector (SVP)
        p : text
            Parameter to modify for the aligment. By default is set to 'both'
            (frame rate and offset). It can be also 'offset'.
        g : text
            Granularity use to do the normalize crosscorrelation. By default
            is set 'notes'. It can be also words, lines, paragraphs
        """
        dist = 0.0
        offset = None
        fr = None
        if self.annotations['type'] != 'horizontal':
            self.vertical2horizontal()
            print("Transforming annots to horizontal format needed for aligning")
        self.info['audio']['path'] = path_audio
        if p == 'both':
            dist, fr, offset = align_brute_force(self, pred=pred, g=g)
        elif p == 'offset':
            dist, offset = align_offset(self, pred=pred, g=g)
        self.change_time(new_offset=offset, new_fr=fr)
        self.info['scores']['NCC'] = dist
        return

    def _prepare_annot_for_change(self):
        t = 'horizontal'
        if self.annotations['type'] == 'vertical':
            t = 'vertical'
            self.vertical2horizontal()
        return t

    def change_time(self, new_offset=None, new_fr=None):
        fr = self.annotations['annot_param']['fr']
        if new_fr is None:
            new_fr = fr
        self.annotations['annot_param']['fr'] = new_fr
        offset = self.annotations['annot_param']['offset']
        if new_offset is None:
            new_offset = offset
        self.annotations['annot_param']['offset'] = new_offset
        t = self._prepare_annot_for_change()
        for key, value in self.annotations['annot'].items():
            value = uta.compute_new_time(value, fr, new_fr, new_offset)
        if t == 'vertical':
            self.horizontal2vertical()
        return

    def change_notes(self, bins_transposition=0, ref_freqs=FREQS):
        t = self._prepare_annot_for_change()
        for key, value in self.annotations['annot'].items():
            value = uta.compute_new_notes(value, bins_transposition)
        if t == 'vertical':
            self.horizontal2vertical()
        return

    def get_annot_as_vector(self, time_r=0.014, dur=0, t='voice', g='notes'):
        """Transforms the annotations into frame vector wrt a time resolution.
        See annot2vector at extra.py for mor info.
        """
        vector = None
        try:
            if not dur:
                dur = end_song(self.info['audio']['path'])
            my_annot = copy.deepcopy(self.annotations['annot'][g])
            vector = annot2vector(my_annot, dur, time_r, t)
        except Exception:
            print("ERROR: no audio track at .info['audio']['path']")
        return vector

    def get_annot_as_vector_chopping(
        self, time_r=6.25e-05, dur=0, win_bin=736, hop_bin=224, t='voice',
        g='notes'
    ):
        """
        Transforms the annotations into a frame vector by:

            1 - creating a vector singal for a give sample rate
            2 - chopping it using the given hop and wind size.
        See annot2vector_chopping at extra.py for mor info.
        """
        vector = None
        try:
            if not dur:
                dur = end_song(self.info['audio']['path'])
            my_annot = copy.deepcopy(self.annotations['annot'][g])
            vector = annot2vector_chopping(
                my_annot, dur, time_r, win_bin, hop_bin, t)
        except Exception:
            print("ERROR: no audio track at .info['audio']['path']")
        return vector

    def get_annot_as_matrix(self, time_r, dur=0, t='notes', g='notes'):
        """Transforms the annotations into frame vector wrt a time resolution.
        See annot2vector at extra.py for mor info.
        """
        matrix = None
        try:
            if not dur:
                dur = end_song(self.info['audio']['path'])
            my_annot = copy.deepcopy(self.annotations['annot'][g])
            matrix = annot2matrix(my_annot, time_r, dur, t)
        except Exception:
            print("ERROR: no audio track at .info['audio']['path']")
        return matrix

    def get_annot_as_pandas(self, g='words'):
        df = None
        try:
            df = annot2pandas(copy.deepcopy(self.annotations['annot'][g]), g)
        except Exception:
            print("ERROR: while computing the pandas")
        return df

    def get_audio(self, path_output):
        self.info['audio']['path'] = audio_from_url(
            self.info['audio']['url'], self.info['id'], path_output)
        return
