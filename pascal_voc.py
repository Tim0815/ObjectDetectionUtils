from pathlib import Path
import os
import sys

# Define IN paths
train_path = '/content/images/train'
val_path = '/content/images/validation'
test_path = '/content/images/test'

# Define OUT paths
pascal_voc_path = '/content/images/pascal_voc'
train_folder = '/train'
val_folder = '/validation'
test_folder = '/test'
images_folder = '/images'
annotation_folder = '/Annotations'


# Get list of all training images
jpeg_file_list = [path for path in Path(train_path).rglob('*.jpeg')]
jpg_file_list = [path for path in Path(train_path).rglob('*.jpg')]
png_file_list = [path for path in Path(train_path).rglob('*.png')]
bmp_file_list = [path for path in Path(train_path).rglob('*.bmp')]

if sys.platform == 'linux':
    JPEG_file_list = [path for path in Path(train_path).rglob('*.JPEG')]
    JPG_file_list = [path for path in Path(train_path).rglob('*.JPG')]
    image_file_list = jpg_file_list + JPG_file_list + png_file_list + bmp_file_list + JPEG_file_list + jpeg_file_list
else:
    image_file_list = jpg_file_list + png_file_list + bmp_file_list + jpeg_file_list

file_num = len(image_file_list)
for i in range(file_num):
    move_me = image_file_list[i]
    fn = move_me.name
    base_fn = move_me.stem
    parent_path = move_me.parent
    xml_fn = base_fn + '.xml'
    os.rename(move_me, pascal_voc_path + train_folder + images_folder + '/' + fn)
    os.rename(os.path.join(parent_path, xml_fn), os.path.join(pascal_voc_path + train_folder + annotation_folder, xml_fn))


# Get list of all validation images
jpeg_file_list = [path for path in Path(val_path).rglob('*.jpeg')]
jpg_file_list = [path for path in Path(val_path).rglob('*.jpg')]
png_file_list = [path for path in Path(val_path).rglob('*.png')]
bmp_file_list = [path for path in Path(val_path).rglob('*.bmp')]

if sys.platform == 'linux':
    JPEG_file_list = [path for path in Path(val_path).rglob('*.JPEG')]
    JPG_file_list = [path for path in Path(val_path).rglob('*.JPG')]
    image_file_list = jpg_file_list + JPG_file_list + png_file_list + bmp_file_list + JPEG_file_list + jpeg_file_list
else:
    image_file_list = jpg_file_list + png_file_list + bmp_file_list + jpeg_file_list

file_num = len(image_file_list)
for i in range(file_num):
    move_me = image_file_list[i]
    fn = move_me.name
    base_fn = move_me.stem
    parent_path = move_me.parent
    xml_fn = base_fn + '.xml'
    os.rename(move_me, pascal_voc_path + val_folder + images_folder + '/' + fn)
    os.rename(os.path.join(parent_path, xml_fn), os.path.join(pascal_voc_path + val_folder + annotation_folder, xml_fn))


# Get list of all test images
jpeg_file_list = [path for path in Path(test_path).rglob('*.jpeg')]
jpg_file_list = [path for path in Path(test_path).rglob('*.jpg')]
png_file_list = [path for path in Path(test_path).rglob('*.png')]
bmp_file_list = [path for path in Path(test_path).rglob('*.bmp')]

if sys.platform == 'linux':
    JPEG_file_list = [path for path in Path(test_path).rglob('*.JPEG')]
    JPG_file_list = [path for path in Path(test_path).rglob('*.JPG')]
    image_file_list = jpg_file_list + JPG_file_list + png_file_list + bmp_file_list + JPEG_file_list + jpeg_file_list
else:
    image_file_list = jpg_file_list + png_file_list + bmp_file_list + jpeg_file_list

file_num = len(image_file_list)
for i in range(file_num):
    move_me = image_file_list[i]
    fn = move_me.name
    base_fn = move_me.stem
    parent_path = move_me.parent
    xml_fn = base_fn + '.xml'
    os.rename(move_me, pascal_voc_path + test_folder + images_folder + '/' + fn)
    os.rename(os.path.join(parent_path, xml_fn), os.path.join(pascal_voc_path + test_folder + annotation_folder, xml_fn))

