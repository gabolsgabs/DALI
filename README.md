
[horizontal]: ./images/horizontal.png
[vertical]: ./images/vertical.png
[p1]: ./images/p1.png
[l1]: ./images/l1.png
[w1]: ./images/w1.png
[Example]: ./images/Example.png


# WELCOME TO THE DALI DATASET: a large **D**ataset of synchronised **A**udio, **L**yr**I**cs and vocal notes.

You can find a detailed explanation of how DALI has been created at:
***[Meseguer-Brocal_2018]*** [G. Meseguer-Brocal, A. Cohen-Hadria and G. Peeters. DALI: a large Dataset of synchronized Audio, LyrIcs and notes, automatically created using teacher-student machine learning paradigm. In ISMIR Paris, France, 2018.](http://ismir2018.ircam.fr/doc/pdfs/35_Paper.pdf)

Cite this paper:

      @inproceedings{Meseguer-Brocal_2018,
      Author = {Meseguer-Brocal, Gabriel and Cohen-Hadria, Alice and Peeters Geoffroy},
      Booktitle = {19th International Society for Music Information Retrieval Conference},
      Editor = {ISMIR},
      Month = {September},
      Title = {DALI: a large Dataset of synchronized Audio, LyrIcs and notes, automatically created using teacher-student machine learning paradigm.},
      Year = {2018}}


Here's an example of the kind of information DALI contains:

![alt text][Example]


DALI has two main elements:

## 1- The dataset - dali_data

The dataset itself. It is denoted as **dali_data** and it is presented as a collection of **gz** files.
You can find the different DALI_data versions in [here](https://github.com/gabolsgabs/DALI/blob/master/versions/).

## 2- The code for working with DALI - dali_code
The code, denoted as **dali_code**, for reading and working with dali_data.
It is stored in this repository and presented as a python package.
Dali_code has its own versions controlled by this github.

repository<br>
├── code<br>
│   ├── DALI<br>
│   │   ├── \_\_init\_\_.py<br>
│   │   ├── Annotations.py<br>
│   │   ├── main.py<br>
│   │   ├── utilities.py<br>
│   │   ├── extra.py<br>
│   │   ├── download.py<br>
│   └── setup.py<br>


# NEWS:

We are working in:
* the second generation for the Singing voice detection system.
* errors in the F0.
* errors in local alignment.

# TUTORIAL:

First of all, [download](https://github.com/gabolsgabs/DALI/blob/master/versions/) your Dali_data version and clone this repository.


## 0- Installing Dali_code.
Go to folder DALI/code and run:

  >  pip install .

You can upgrade DALI for future version with:

  >  pip install . --upgrade

DALI can be uninstalled with:

  >  pip uninstall DALI-dataset

Requirements: **numpy** and **youtube_dl**

**NOTE**: the version of the code in pip only refers to the code itself. The different versions of the Dali_data can be found above.


## 1- Loading DALI_data.

DALI is presented as a set of **gz** files.
Each gz contains the annotations of a particular song.
We use a unique id for each entry.
You can download your dali_data version as follow:

    import DALI as dali_code
    dali_data_path = 'full_path_to_your_dali_data'
    dali_data = dali_code.get_the_DALI_dataset(dali_data_path, skip=[], keep=[])

This function can also be used to load a subset of the DALI dataset by providing the ids of the entries you either want to **skip** or to **keep**.

**NOTE**: Loading DALI might take some minutes depending on your computer and python version.

Additionally, each DALI version contains a DALI_DATA_INFO.gz:

    dali_info = dali_code.get_info(dali_data_path + 'info/DALI_DATA_INFO.gz')
    print(dali_info[0]) -> array(['DALI_ID', 'NAME', 'YOUTUBE', 'WORKING'])

This file matches the unique DALI id with the artist_name-song_tile, the url to youtube and a bool that says if the youtube link is working or not.  

<!--- This file is updated with -->

### An annotation instance.

_dali_data_ is a dictionary where each key is a unique id and the value is an instance of the class DALI/Annotations namely **an annotation instance** of the class Annotations.

    entry = dali_data['a_dali_unique_id']
    type(entry) -> DALI.Annotations.Annotations

Each annotation instance has two attributes: **info** and **annotations**.

    entry.info --> {'id': 'ffa06527f9e84472ba44901045753b4a',
                    'artist': 'An Artist',
                    'title': 'A song title',
                    'dataset_version': 1.0,     **# dali_data version**
                    'ground-truth': 'None',     **# Not ready yet**
                    'scores': {'NCC': 0.8098520072498807,
                               'manual': 0.0},  **# Not ready yet**
                    'audio': {'url': 'a youtube url',
                              'path': 'None',   
                              **# To be modified to point to your local audio file**
                              'working': True},
                    'metadata': {'album': 'An album title',
                                 'release_date': 'A year',
                                 'cover': 'link to a image with the cover',
                                 'genres': ['genre_0', ... , 'genre_n'],
                                 # The n of genre depends on the song
                                 'language': 'a language'}}

    entry.annotations --> {'annot': {'the annotations themselves'},
                           'type': 'horizontal' or 'vertical',
                           'annot_param': {'fr': float(frame rate used in the annotation process),
                                          'offset': float(offset value)}}


# 2- Getting the audio.

You can retrieve the audio for each annotation (if avilable) using the function dali_code.get_audio():

    errors = dali_code.get_audio(dali_info, 'full_path_to_store_the_audio', skip=[], keep=[])
    errors -> ['dali_id', 'youtube_url', 'error']

This function can also be used to download a subset of the DALI dataset by providing the ids of the entries you either want to **skip** or to **keep**.


# 3- Working with DALI.

Annotations are in:
> entry.annotations['annot']

and they are presented in two different formats: **'horizontal'** or **'vertical'**.
You can easily change the format using the functions:

      entry.horizontal2vertical()
      entry.vertical2horizontal()

## 3.1- Horizontal.
In this format each level of granularity is stored individually.
It is the default format.

![alt text][horizontal]

    entry.vertical2horizontal() --> 'Annot are already in a vertical format'
    entry.annotations['type'] --> 'horizontal'
    entry.annotations['annot'].keys() --> ['notes', 'lines', 'words', 'paragraphs']

Each level contains a list of annotation where each element has:

    my_annot = entry.annotations['annot']['notes']
    my_annot[0] --> {'text': 'wo', # the annotation itself.
                     'time': [12.534, 12.659], # the begining and end of the  segment in seconds.
                     'freq': [466.1637615180899, 466.1637615180899], # The range of frequency the text information is covering. At the lowest level, syllables, it corresponds to the vocal note.
                     'index': 0} # link with the upper level. For example, index 0 at the 'words' level means that that particular word below to first line ([0]). The paragraphs level has no index key.

### 3.1.1- Vizualizing the annotations.

You can export the annotations of each individual level to a xml or text file to vizualize them with Audacity or AudioSculpt. The pitch information is only presented in the xml files for AudioSculpt.

        my_annot = entry.annotations['annot']['notes']
        path_save = 'my_save_path'
        dali_code.write_annot_txt(my_annot, 'my_annot', path_save)
        # import the txt file in your Audacity
        dali_code.write_annot_xml(my_annot, 'my_annot', path_save)
        # import Rythm XML file in AudioSculpt


### 3.1.2- Examples.
This format is ment to be use for working with each level individually.
> Example 1: recovering the main vocal melody.

Let's used the extra function dali_code.annot2vector() that transforms the annotations into a vector. There are two types of vector:

- type='voice': each frame has a value 1 or 0 for voice or not voice.
- type='melody': each frame has the freq value of the main vocal melody.

      my_annot = entry.annotations['annot']['notes']
      time_resolution = 0.014
      # the value dur is just an example you should use the end of your audio file
      end_of_the_song =  entry.annotations['annot']['notes'][-1]['time'][1] + 10
      melody = dali_code.annot2vector(my_annot, end_of_the_song, time_resolution, type='melody')

**NOTE: have a look to dali_code.annot2vector_chopping() for computing a vector chopped with respect to a given window and hop size.**

> Example 2: find the audio frames that define each paragraph.

Let's used the other extra function dali_code.annot2frames() that transforms time in seconds into time in frames.

      my_annot = entry.annotations['annot']['paragraphs']
      paragraphs = [i['time'] for i in annot2frames(my_annot, time_resolution)]
      paragraphs --> [(49408, 94584), ..., (3080265, 3299694)]


**NOTE**: dali_code.annot2frames() can also be used in the vertical format but not dali_code.annot2vector().

## 3.2- Vertical.
In this format the different levels of granularity are hierarchically connected:

![alt text][vertical]

      entry.horizontal2vertical()
      entry.annotations['type'] --> 'vertical'
      entry.annotations['annot'].keys() --> ['hierarchical']
      my_annot = entry.annotations['annot']['hierarchical']

Each element of the list is a paragraph.

      my_annot[0] --> {'freq': [277.1826309768721, 493.8833012561241], # The range of frequency the text information is covering
                       'time': [12.534, 41.471500000000006], # the begining and end of the time segment.
                       'text': [line_0, line_1, ..., line_n]}

![alt text][p1]

where 'text' contains all the lines of the paragraph. Each line follows the same format:

      lines_1paragraph = my_annot[0]['text']
      lines_1paragraph[0] --> {'freq': [...], 'time': [...],
                               'text': [word_0, word_1, ..., word_n]}

![alt text][l1]

again, each word contains all the notes for that word to be sung:

      words_1line_1paragraph = lines_first_paragraph[0]['text']
      words_1line_1paragraph[0] --> {'freq': [...], 'time': [...],
                                     'text': [note_0, note_1, ..., note_n]}

![alt text][w1]

Only the deepest level directly has the text information.

      notes_1word_1line_1paragraph = words_1line_1paragraph[1]['text']
      notes_1word_1line_1paragraph[0] --> {'freq': [...], 'time': [...],
                                           'text': 'note text'}

You can always get the text at specific point with dali_code.get_text(), i.e:

      dali_code.get_text(lines_1paragraph) --> ['text word_0', 'text word_1', ..., text_word_n]
      # words in the first line of the first paragraph

      dali_code.get_text(my_annot[0]['text']) --> ['text word_0', 'text word_1', ..., text_word_n]
      # words in the first paragraph

### 3.2.2- Examples.
This organization is meant to be used for working with specific hierarchical blocks.

> Example 1: working only with the third paragraph.

      my_paragraph = my_annot[3]['text']
      text_paragraph = dali_code.get_text(my_paragraph)

Additionally, you can easily retrieve all its individual information with the function dali_code.unroll():

      lines_in_paragraph, _ = dali_code.unroll(my_paragraph, depth=0, output=[])
      words_in_paragraph, _ = dali_code.unroll(my_paragraph, depth=1, output=[])
      notes_in_paragraph, _ = dali_code.unroll(my_paragraph, depth=2, output=[])

> Example 2: working only with the first line of the third paragraph

      my_line = my_annot[3]['text'][0]['text']
      text_line = dali_code.get_text(my_line)
      words_in_line, _ = dali_code.unroll(my_line, depth=0, output=[])
      notes_in_line, _ = dali_code.unroll(my_line, depth=1, output=[])

_____
If you have any question you can contact us at:

> dali dot dataset at gmail dot com
