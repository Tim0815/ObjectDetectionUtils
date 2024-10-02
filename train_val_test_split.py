### Python script to split a labeled image dataset into Train, Validation, and Test folders.
# Author: Evan Juras, EJ Technology Consultants
# Date: 4/10/21

# Randomly splits images to 88% train, 10% validation, and 2% test, and moves them to their respective folders. 
# This script is intended to be used in the TFLite Object Detection Colab notebook here:
# https://colab.research.google.com/github/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/Train_TFLite2_Object_Detction_Model.ipynb

from pathlib import Path
import random
import os
import sys
import re


# Define paths to image folders
image_path = '/content/images/all'
train_path = '/content/images/train'
val_path = '/content/images/validation'
test_path = '/content/images/test'

Path(train_path).mkdir(parents=True, exist_ok=True)
Path(val_path).mkdir(parents=True, exist_ok=True)
Path(test_path).mkdir(parents=True, exist_ok=True)


# Get list of all images
jpeg_file_list = [path for path in Path(image_path).rglob('*.jpeg')]
jpg_file_list = [path for path in Path(image_path).rglob('*.jpg')]
png_file_list = [path for path in Path(image_path).rglob('*.png')]
bmp_file_list = [path for path in Path(image_path).rglob('*.bmp')]

if sys.platform == 'linux':
    JPEG_file_list = [path for path in Path(image_path).rglob('*.JPEG')]
    JPG_file_list = [path for path in Path(image_path).rglob('*.JPG')]
    file_list = jpg_file_list + JPG_file_list + png_file_list + bmp_file_list + JPEG_file_list + jpeg_file_list
else:
    file_list = jpg_file_list + png_file_list + bmp_file_list + jpeg_file_list

file_num = len(file_list)
print('Total images: %d' % file_num)

# Determine number of files to move to each folder
train_percent = 0.88  # 88% of the files go to train
val_percent = 0.10 # 10% go to validation
test_percent = 0.02 # 2% go to test
train_num = int(file_num*train_percent)
val_num = int(file_num*val_percent)
test_num = file_num - train_num - val_num


def handleFile(new_path):
    move_me = random.choice(file_list)
    fn = move_me.name
    base_fn = move_me.stem
    parent_path = move_me.parent
    parent_dir_suffix = os.path.basename(parent_path) + '_'
    os.rename(move_me, os.path.join(new_path, parent_dir_suffix + fn))
    xml_fn = base_fn + '.xml'
    xml_me = os.path.join(parent_path, xml_fn)
    if (os.path.isfile(xml_me)):
        with open(xml_me, 'r+') as fxml:
            xml_content = fxml.read()
            xml_content = re.sub('<filename>' + fn + '</filename>', '<filename>' + parent_dir_suffix + fn + '</filename>', xml_content)
            fxml.truncate(0)
            fxml.write(xml_content)
        os.rename(xml_me, os.path.join(new_path, parent_dir_suffix + xml_fn))
    file_list.remove(move_me) 


# Select 88% of files randomly and move them to train folder
print('Images moving to train: %d' % train_num)
for i in range(train_num):
    handleFile(train_path)


# Select 10% of remaining files and move them to validation folder
print('Images moving to validation: %d' % val_num)
for i in range(val_num):
    handleFile(val_path)


# Move remaining files to test folder
print('Images moving to test: %d' % test_num)
for i in range(test_num):
    handleFile(test_path)

