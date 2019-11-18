import librosa


PHONEMES_DICT = {
    'AA': 'vowel', 'AE': 'vowel', 'AH': 'vowel', 'AO': 'vowel', 'AW': 'vowel',
    'AY': 'vowel', 'B': 'stop', 'CH': 'affricate', 'D': 'stop',
    'DH': 'fricative', 'EH': 'vowel', 'ER': 'vowel', 'EY': 'vowel',
    'F': 'fricative', 'G': 'stop', 'HH': 'aspirate', 'IH': 'vowel',
    'IY': 'vowel', 'JH': 'affricate', 'K': 'stop', 'L': 'liquid', 'M': 'nasal',
    'N': 'nasal', 'NG': 'nasal', 'OW': 'vowel', 'OY': 'vowel', 'P': 'stop',
    'R': 'liquid', 'S': 'fricative', 'SH': 'fricative', 'T': 'stop',
    'TH': 'fricative', 'UH': 'vowel', 'UW': 'vowel', 'V': 'fricative',
    'W': 'semivowel', 'Y': 'semivowel', 'Z': 'fricative', 'ZH': 'fricative'
}

PHONEMES = list(PHONEMES_DICT.keys())
PHONEMES_TYPE = []

for i in PHONEMES_DICT.values():
    if i not in PHONEMES_TYPE:
        PHONEMES_TYPE.append(i)


CHAR = [" ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "'"]


BINS_PER_OCTAVE = 36
BINS_PER_SEMITONE = 3
N_OCTAVES = 6
SR = 22050
FMIN = 40
HOP_LENGTH = 256
FREQS = librosa.cqt_frequencies(
    n_bins=N_OCTAVES * BINS_PER_OCTAVE, fmin=FMIN,
    bins_per_octave=BINS_PER_OCTAVE)
