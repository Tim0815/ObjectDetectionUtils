from sys import argv
from pathlib import Path
from PIL import Image
import os

image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)


# Converting PNG files:
png_file_list = [path for path in Path(image_path).rglob('*.png')]
num_files = len(png_file_list)
if (num_files == 0):
    print('No JPEG images found in folder.')
else:
    print('Converting ' + str(num_files) + ' PNG images...')

    for file in png_file_list:
        origFile = file
        im = Image.open(file)
        rgb_im = im.convert('RGB')
        rgb_im.save(file.with_suffix('.jpg'))
        os.remove(origFile)


# Renaming JPEG files:
jpeg_file_list = [path for path in Path(image_path).rglob('*.jpeg')]
num_files = len(jpeg_file_list)
if (num_files == 0):
    print('No JPEG images found in folder.')
else:
    print('Renaming ' + str(num_files) + ' JPEG images...')

    for file in jpeg_file_list:
        file.rename(file.with_suffix('.jpg'))


print('Complete.')
