"""LOADING DALI DATASET FUNCTIONS:

Functions for loading the Dali dataset.

GABRIEL MESEGUER-BROCAL 2018
"""
from . import utilities as ut
# from .Annotations import Annotations

# ------------------------ READING INFO ------------------------


def generator_files_skip(file_names, skip=[]):
    """Generator with all the file to read.
    It skips the files in the skip ids list"""
    for fl in file_names:
        if fl.split('/')[-1].rstrip('.gz') not in skip:
            yield ut.read_gzip(fl)


def generator_files_in(file_names, keep=[]):
    """Generator with all the file to read.
    It reads only the files in the keep ids list"""
    for fl in file_names:
        if fl.split('/')[-1].rstrip('.gz') in keep:
            yield ut.read_gzip(fl, print_error=True)


def generator_folder(folder_pth, skip=[], keep=[]):
    """Create the final Generator with all the files."""
    if len(keep) > 0:
        return generator_files_in(ut.get_files_path(folder_pth,
                                                    print_error=True), keep)
    else:
        return generator_files_skip(ut.get_files_path(folder_pth,
                                                      print_error=True), skip)


def change_time(entry, new_offset=None, new_fr=None):
    type = 'horizontal'
    fr = entry.annotations['annot_param']['fr']
    offset = entry.annotations['annot_param']['offset']
    if new_fr is None:
        new_fr = fr
    if new_offset is None:
        new_offset = offset
    args = (fr, offset, new_fr, new_offset)
    entry.annotations['annot_param']['fr'] = new_fr
    entry.annotations['annot_param']['offset'] = new_offset
    if entry.annotations['type'] == 'vertical':
        type = 'vertical'
        entry.vertical2horizontal()
    for key, value in entry.annotations['annot'].items():
        value = ut.compute_new_time(value, *args)
    if type == 'vertical':
        entry.horizontal2vertical()
    return


def update_with_ground_truth(dali, gt_file):
    gt = []
    if ut.check_file(gt_file, print_error=False):
        gt = load_ground_truth(gt_file)
    if len(gt) > 0:
        for i in gt:
            entry = dali[i]
            change_time(entry, gt[i]['offset'], gt[i]['fr'])
            entry.info['ground-truth'] = True
    return dali


def get_the_DALI_dataset(pth, gt_file='', skip=[], keep=[]):
    """Load the whole DALI dataset. It can load only a subset of the dataset
    by providing either the ids to skip or the ids that to load."""
    args = (pth, skip, keep)
    dali = {song.info['id']: song for song in generator_folder(*args)}
    dali = update_with_ground_truth(dali, gt_file)
    return dali


def get_an_entry(fl_pth):
    """Retrieve a particular entry and return as a class."""
    return ut.read_gzip(fl_pth)


def get_info(dali_info_file):
    """Read the DALI INFO file with ['DALI_ID', 'YOUTUBE_ID', 'WORKING']
    """
    return ut.read_gzip(dali_info_file, print_error=True)


def load_ground_truth(dali_gt_file):
    """Read the ground_truth file
    """
    return ut.read_gzip(dali_gt_file, print_error=True)

# ------------------------ BASIC OPERATIONS ------------------------


def update_audio_working_from_info(info, dali_dataset):
    """Update the working label for each class using a info file"""
    for i in info[1:]:
        dali_dataset[i[0]].info['audio']['working'] = i[-1]
    return dali_dataset


def ids_to_title_artist(dali_dataset):
    """Transform the unique DALI id to """
    output = [[value.info['id'], value.info['artist'], value.info['title']]
              for key, value in dali_dataset.items()]
    output.insert(0, ['id', 'artist', 'title'])
    return output
