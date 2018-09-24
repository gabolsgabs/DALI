
[DALI]: ./images/DALI.png

![alt text][DALI]

# WELCOME TO THE DALI DATASET: a large **D**ataset of synchronised **A**udio, **L**yr**I**cs and vocal notes.

You can find a detailed explanation of how DALI has been created at:
***[Meseguer-Brocal_2018]*** [G. Meseguer-Brocal, A. Cohen-Hadria and G. Peeters. DALI: a large Dataset of synchronized Audio, LyrIcs and notes, automatically created using teacher-student machine learning paradigm. In ISMIR Paris, France, 2018.](http://ismir2018.ircam.fr/doc/pdfs/35_Paper.pdf)



__Download the Ismir 2018 preview__ [here](https://github.com/gabolsgabs/DALI/blob/master/ismir_preview.zip)

In this example you will find:

- 'audio': id to the youtube video
- 'annotations': lyrics aligned in time at four different level of granularity: 'syllables', 'words', 'lines', 'paragraphs'. Each annotaion has:
    - 'text': the annotation itself.
    - 'time': the begining and end of the time segment.
    - 'freq': the range of frequency the text information is covering. At the lowest level,
    syllables, it corresponds to the vocal note.
    - 'index': link with the upper level. For example, index 0 at the 'words' level means that that particular word below to first line ([0]). The paragraphs level has no index key.

__The dataset format is a working process. Please send your feedbacks at gabriel.meseguerbrocal (at) ircam.fr and help us to improve DALI.__
