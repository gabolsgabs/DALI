"""LOADING DALI DATASET FUNCTIONS:

Functions for loading the Dali dataset.

GABRIEL MESEGUER-BROCAL 2018
"""
import utilities as ut
from DALI.Annotations import Annotations

# ------------------------ READING INFO ------------------------


def generator_files_skip(file_names, skip=[]):
    """Generator with all the file to read.
    It skips the files in the skip ids list"""
    for fl in file_names:
        if fl.split('/')[-1].rstrip('.gz') not in skip:
            yield ut.read_gzip(fl)


def generator_files_in(file_names, in_list=[]):
    """Generator with all the file to read.
    It reads only the files in the in_list ids list"""
    for fl in file_names:
        if fl.split('/')[-1].rstrip('.gz') in in_list:
            yield ut.read_gzip(fl)


def generator_folder(folder_pth, skip=[], in_list=[]):
    """Create the final Generator with all the files."""
    if len(in_list) > 0:
        return generator_files_in(ut.get_files_path(folder_pth), in_list)
    else:
        return generator_files_skip(ut.get_files_path(folder_pth), skip)


def get_the_DALI_dataset(pth, skip=[], in_list=[]):
    """Load the whole DALI dataset. It can load only a subset of the dataset
    by providing either the ids to skip or the ids that to load."""
    args = (pth, skip, in_list)
    return {song.info['id']: song for song in generator_folder(*args)}


def get_an_entry(fl_pth):
    """Retrieve a particular entry and return as a class."""
    return ut.read_gzip(fl_pth)


def get_info(pth):
    """Read the DALI INFO file with ['DALI_ID', 'YOUTUBE_ID', 'WORKING']
    """
    info = None
    try:
        info = ut.read_json([i for i in get_files_path(pth, '*.json')
                             if 'DALI_INFO' in i][0])
    except Exception as e:
        print('ERROR: not DALI_INFO in your folder')
    return info

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
