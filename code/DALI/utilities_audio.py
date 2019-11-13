""" Utilities functions for dealing with the dali dataset.

It includes all the needed functions for reading files and the helpers for
transforming the annotation information.

GABRIEL MESEGUER-BROCAL 2018
"""
import numpy as np
import os
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
            except Exception as e:
                s = 0
        if 'duration' in i:
            d = np.float(i.split("=")[1])
    return d - s


def read_MP3(audio, sr_hz=16000., stereo2mono=False):
    """Transform any audio format into mp3 - ALICE VERSION"""
    if os.path.isfile(audio):
        if (audio.endswith('mp3') | audio.endswith('aif')
            | audio.endswith('aiff') | audio.endswith('wav')
            | audio.endswith('ogg') | audio.endswith('flac')):
            # --- resample and reduce to mono
            if stereo2mono:
                ffmpeg = sp.Popen(
                    ["ffmpeg", "-i", audio, "-vn", "-acodec",
                     "pcm_s16le", "-ac", "1", "-ar", str(sr_hz), "-f", "s16le",
                     "-"], stdin=sp.PIPE, stdout=sp.PIPE,
                    stderr=open(os.devnull, "w"))
            else:
                # --- resample and keep stereo
                ffmpeg = sp.Popen(
                    ["ffmpeg", "-i", audio, "-vn", "-acodec",
                     "pcm_s16le", "-ac", "2", "-ar", str(sr_hz), "-f",
                     "s16le", "-"], stdin=sp.PIPE, stdout=sp.PIPE,
                    stderr=open(os.devnull, "w"))
            raw_data = ffmpeg.stdout
            mp3_array = np.fromstring(raw_data.read(), np.int16)
            mp3_array = mp3_array.astype('float32') / 32767.0
            data_v = mp3_array.view()
            if not stereo2mono:
                data_v = np.reshape(data_v, (int(data_v.shape[0]/2), 2))
            return data_v, sr_hz
