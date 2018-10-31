from DALI.Annotations import Annotations
import os
from . import utilities as ut
import xml.etree.ElementTree as ET


sculpt_segment_tag = '{http://www.ircam.fr/musicdescription/1.1}segment'
sculpt_freetype_tag = '{http://www.ircam.fr/musicdescription/1.1}freetype'
sculpt_media_tag = '{http://www.ircam.fr/musicdescription/1.1}media'
ET.register_namespace('', "http://www.ircam.fr/musicdescription/1.1")
pth = os.path.dirname(os.path.abspath(__file__))
xml_template = os.path.join(pth, 'files/template.xml')

# ----------------------------------XML-------------------------------


def addsemgnet(parent, text, attrib, tag=sculpt_segment_tag,
               sub_tag=sculpt_freetype_tag):

    element = parent.makeelement(tag, attrib)
    sub = ET.SubElement(element, sub_tag)
    sub.attrib['value'] = text
    sub.attrib['id'] = '1'
    parent.append(element)
    # element.text = text
    return


def create_xml_attrib(annot):
    point = {'startFreq': '', 'endFreq': '', 'length': '', 'sourcetrack': '0',
             'time': ''}
    offset = 0
    if annot['freq'][0] == annot['freq'][1]:
        offset = 20

    point['time'] = str(annot['time'][0])
    point['length'] = str(annot['time'][1] - annot['time'][0])
    point['startFreq'] = str(annot['freq'][0] - offset)
    point['endFreq'] = str(annot['freq'][1] + offset)
    return point


def write_annot_xml(annot, name, path_save, xml_template=xml_template):
    path_save = ut.create_directory(path_save)
    tree = ET.parse(xml_template)
    root = tree.getroot()
    media = root.findall(sculpt_media_tag)[0]
    media.text = name

    # print ET.tostring(root)
    # segments = root.findall(sculpt_segment_tag)

    for point in annot:
        addsemgnet(root, point['text'], attrib=create_xml_attrib(point))

    """
    for line in segmented_lyrics.lines:
        addsemgnet(root, line['text'], attrib=create_xml_attrib(line))
    for word in segmented_lyrics.words:
        addsemgnet(root, word['text'], attrib=create_xml_attrib(word))
    """

    segment = root.findall(sculpt_segment_tag)
    root.remove(segment[0])
    # tree.write(name.replace("wav", "xml"))
    tree.write(os.path.join(path_save, name + ".xml"))
    return


# ------------------------------TXT-------------------------------


def write_annot_txt(annot, name, path_save):
    path_save = ut.create_directory(path_save)
    with open(os.path.join(path_save, name + ".txt"), 'w') as f:
        for item in annot:
            f.write("%f\t" % item['time'][0])
            f.write("%f\t" % item['time'][1])
            f.write("%s\n" % item['text'])
    return
