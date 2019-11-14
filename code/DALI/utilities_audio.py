""" Utilities functions for dealing with the dali dataset.

It includes all the needed functions for reading files and the helpers for
transforming the annotation information.

GABRIEL MESEGUER-BROCAL 2018
"""
import numpy as np
import subprocess as sp

# ------------------------ AUDIO ----------------


def end_song(filename):
    """Get duration from a given audio"""
    args = ("ffprobe", "-show_entries", "format=duration,start_time", "-i",
            filename)
    popen = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
    popen.wait()
    output = popen.stdout.read()
    if isinstance(output, bytes):
        output = output.decode('utf-8')
    s = 0.0
    d = 0.0
    for i in output.split("\n"):
        if 'start_time' in i:
            try:
                s = np.float(i.split("=")[1])
            except Exception:
                s = 0
        if 'duration' in i:
            d = np.float(i.split("=")[1])
    return d - s
