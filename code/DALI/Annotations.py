""" ANNOTATIONS class.

GABRIEL MESEGUER-BROCAL 2018
"""
from .extra import (unroll, roll)
from . import utilities as ut


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
