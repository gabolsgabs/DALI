
[DALI]: ./images/DALI_small.png
[Example]: ./images/Example.png


# WELCOME TO THE DALI DATASET: a large **D**ataset of synchronised **A**udio, **L**yr**I**cs and vocal notes.

You can find a detailed explanation of how DALI has been created at:
***[Meseguer-Brocal_2018]*** [G. Meseguer-Brocal, A. Cohen-Hadria and G. Peeters. DALI: a large Dataset of synchronized Audio, LyrIcs and notes, automatically created using teacher-student machine learning paradigm. In ISMIR Paris, France, 2018.](http://ismir2018.ircam.fr/doc/pdfs/35_Paper.pdf)

Cite this paper:

      @inproceedings{Meseguer-Brocal_2018,
      Author = {Meseguer-Brocal, Gabriel and Cohen-Hadria, Alice and Gomez and Peeters Geoffroy},
      Booktitle = {19th International Society for Music Information Retrieval Conference},
      Editor = {ISMIR},
      Month = {September},
      Title = {DALI: a large Dataset of synchronized Audio, LyrIcs and notes, automatically created using teacher-student machine learning paradigm.},
      Year = {2018}}


Here's an example of the kind of information DALI contains:

![alt text][Example]


DALI has two main elements:

#### 1- The dataset.

You can find the different versions and the link for download them in [here](https://github.com/gabolsgabs/DALI/blob/master/versions/).

#### 2- The code for working with DALI.
This repository provides (DALI/code) a small python package for working with DALI.

## NEWS:

<!--- POSSIBLE ERRORS IN THE F0 of the singing voice-->

## TUTORIAL:

Once you have a DALI [version](https://github.com/gabolsgabs/DALI/blob/master/versions/)  here's a tutorial with the basic steps for working with this dataset.

### Installation.
Clone this repository, go to folder DALI/code and run:

  >  pip install .

You can upgrade DALI for future version with:

  >  pip install . --upgrade

DALI can be uninstalled with:

  >  pip uninstall DALI-dataset

Requirements: **numpy**

**NOTE**: the version of the code in pip only refers to the code itself. The different versions of the DALI dataset (annotations) can be found above.

### Loading DALI.

DALI is presented as a set of **gz** files.
Each one contains the annotations of a particular song.
We use a unique id for each entry.
Once a DALI version is downloaded you can load it as follow:

    import DALI
    dali = DALI.main.get_the_DALI_dataset('path_to_dali', skip=[], keep=[])

This function can also be used to load a subset of the DALI dataset by providing the ids of the entries you either want to **skip** or to **keep**.

**NOTE**: Loading DALI might take some minutes depending on your computer and python version.

Each DALI version contains a DALI_INFO.gz:

    info = DALI.main.get_info('path_to_dali/info/DALI_INFO.gz')
    print(info[0]) -> array(['DALI_ID', 'NAME', 'YOUTUBE', 'WORKING'])

This file connects the unique DALI id with the artist_name-song_tile, the url to youtube and a bool that says if the youtube link is working or not.  

<!--- This file is updated with -->

### Working with DALI.

Each entry of the DALI dataset is an instance of the class DALI/Annotations.

    import copy
    entry = copy.deepcopy(dali['a_dali_unique_id'])
    type(entry) -> DALI.Annotations.Annotations

It has two main attributes: **info** and **annotations**.

    entry.info --> {'id': 'ffa06527f9e84472ba44901045753b4a',
                    'artist': 'An Artist',
                    'title': 'A song title',
                    'dataset_version': 1.0,
                    'ground-truth': 'None',     # Not ready yet
                    'scores': {'NCC': 0.8098520072498807,
                               'manual': 0.0},  # Not ready yet
                    'audio': {'url': 'a youtube url',
                              'path': 'None',   
                              # To be modified to point to your local audio file
                              'working': True},
                    'metadata': {'album': 'An album title',
                                 'release_date': 'A year',
                                 'cover': 'link to a image with the cover',
                                 'genres': ['genre_0', ... , 'genre_n'],
                                 # The n of genre depends on the song
                                 'language': 'a language'}}

    entry.annotations --> {'annot': {'the annotations'},
                           'type': 'horizontal' or 'vertical',
                           'annot_param': {'fr': float(frame rate used in the annotation process),
                                          'offset': float(offset value)}}

Annotations are in:
> entry.annotations['annot']

and they can be presented in two format: 'horizontal' or 'vertical'.
You can easily change the format using the functions:

      entry.horizontal2vertical()
      entry.vertical2horizontal()

#### Horizontal.
In this format each level of granularity is stored indivually:

    entry.annotations['type'] --> 'horizontal'
    entry.annotations['annot'].keys() --> ['notes', 'lines', 'words', 'paragraphs']

Each level contains a list of annotation where each element has:

    my_annot = entry.annotations['annot']['notes']
    my_annot[0] --> {'text': 'wo', # the annotation itself.
                     'time': [12.534, 12.659], # the begining and end of the  segment in seconds.
                     'freq': [466.1637615180899, 466.1637615180899], # The range of frequency the text information is covering. At the lowest level, syllables, it corresponds to the vocal note.
                     'index': 0} # link with the upper level. For example, index 0 at the 'words' level means that that particular word below to first line ([0]). The paragraphs level has no index key.

This format is ment to be use when you want to work with each level indivually.

> Example 1: recovering the main vocal melody. Let's used the extra function DALI.Annotations.annot2vector() that transforms the annotations into a vector. There are two types of vector:

- type='voice': each frame has a value 1 or 0 for voice or not voice.
- type='notes': each frame has the freq value of the main vocal melody.

      my_annot = entry.annotations['annot']['notes']
      time_resolution = 0.014
      # the value dur is just an example you should use the end of your audio file
      end_of_the_song =  entry.annotations['annot']['notes'][-1]['time'][1] + 10
      melody = DALI.Annotations.annot2vector(my_annot, time_resolution, type='notes')

**NOTE: have a look to annot2vector_chopping() for computing a vector chopped with respect to a given window and hop size.**

> Example 2: find the audio frames that define each paragraph. Let's used the other extra function DALI.Annotations.annot2frames() that transforms time in seconds into time in frames.

      my_annot = entry.annotations['annot']['paragraphs']
      paragraphs = [i['time'] for i in annot2frames(my_annot, time_resolution)]
      paragraphs --> [(49408, 94584), ..., (3080265, 3299694)]


**NOTE**: DALI.Annotations.annot2frames() can also be used in the vertical format but not DALI.Annotations.annot2vector().

#### Vertical.
In this format the different levels of granularity are hierarchically connected:

      entry.annotations['type'] --> 'vertical'
      entry.annotations['annot'].keys() --> ['hierarchical']
      my_annot = entry.annotations['annot']['hierarchical']

Each element of the list is a paragraph.

      my_annot[0] --> {'freq': [277.1826309768721, 493.8833012561241], # The range of frequency the text information is covering
                       'time': [12.534, 41.471500000000006], # the begining and end of the time segment.
                       'text': [line_0, line_1, ..., line_n]}

where 'text' contains all the lines of the paragraph. Each line follows the same format:

      lines_1paragraph = my_annot[0]['text']
      lines_1paragraph[0] --> {'freq': [...], 'time': [...],
                               'text': [word_0, word_1, ..., word_n]}

again, each word contains all the notes for that word to be sung:

      words_1line_1paragraph = lines_first_paragraph[0]['text']
      words_1line_1paragraph[0] --> {'freq': [...], 'time': [...],
                                     'text': [note_0, note_1, ..., note_n]}

Only the deepest level directly has the text information.

      notes_1word_1line_1paragraph = words_1line_1paragraph[0]['text']
      notes_1word_1line_1paragraph[0] --> {'freq': [...], 'time': [...],
                                           'text': 'note text'}

But you can always get the text of a specific point with DALI.utilities.get_text(), i.e:

      DALI.utilities.get_text(lines_1paragraph) --> ['text word_0', 'text word_1', ..., text_word_n]
      # words in the first line of the first paragraph

      DALI.utilities.get_text(my_annot[0]['text']) --> ['text word_0', 'text word_1', ..., text_word_n]
      # words in the first paragraph

This organization is meant to be used for working only with a specific block.

> Example 1: working only with the third paragraph.

      my_paragraph = my_annot[3]['text']
      text_paragraph = DALI.utilities.get_text(my_paragraph)

Additionally, you can easily retrieve all its individual information with the function DALI.utilities.unroll():

      lines_in_paragraph, _ = DALI.utilities.unroll(my_paragraph, depth=0, output=[])
      words_in_paragraph, _ = DALI.utilities.unroll(my_paragraph, depth=1, output=[])
      notes_in_paragraph, _ = DALI.utilities.unroll(my_paragraph, depth=2, output=[])

> Example 2: working only with the first line of the third paragraph

      my_line = my_annot[3]['text'][0]['text']
      text_line = DALI.utilities.get_text(my_line)
      words_in_line, _ = DALI.utilities.unroll(my_line, depth=0, output=[])
      notes_in_line, _ = DALI.utilities.unroll(my_line, depth=1, output=[])

If you have any question you can contact us at:

> dali dot dataset at gmail dot com

![alt text][DALI]
