import os
import argparse
from optparse import OptionParser
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from math import floor
from pathlib import Path


# Update XML file if it exists:
def updateXml(xml_file_name, new_label):
    if os.path.isfile(xml_file_name):
        xmlRoot = ET.parse(xml_file_name).getroot()
        for member in xmlRoot.findall('object'):
            member.find('name').text = new_label
        tree = ET.ElementTree(xmlRoot)
        tree.write(xml_file_name)


parser = argparse.ArgumentParser()

parser.add_argument(
    '-p',
    '--path',
    dest='dataset_path',
    help='Path to dataset data ?(image and annotations).',
    default='.',
    required=False
)

parser.add_argument(
    '-l',
    '--label',
    dest='new_label',
    help='The new class label to be used for all images',
    required=True
)


args = parser.parse_args()

image_path = args.dataset_path
if (image_path is None or image_path == '.'):
    image_path = os.getcwd()

new_label = args.new_label
if (new_label is None or new_label == '.'):
    print('New class label must be given! Use argument -l NEW_LABEL for new label name.')
else:
    new_label = new_label.lower()
    print('Folder: ' + image_path + ', new label: \"' + new_label + '\"')
    annotation_files_list = [path for path in Path(image_path).rglob('*.xml')]
    num_files = len(annotation_files_list)
    if (num_files == 0):
        print('No XML annotation files found in folder.')
    else:
        print('Converting ' + str(num_files) + ' XML annotation files...')

        for file in annotation_files_list:
            updateXml(file, new_label)
    print('Conversion complete.')
