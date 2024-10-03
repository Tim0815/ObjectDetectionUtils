from sys import argv
from pathlib import Path
from PIL import Image
import os
import xml.etree.ElementTree as ET


image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)


# Update XML file if it exists:
def updateXml(file_name):
    folder = Path(file_name).parent
    fn = Path(file_name).stem
    xml_path = os.path.join(folder, fn + '.xml')
    if os.path.isfile(xml_path):
        xmlRoot = ET.parse(xml_path).getroot()
        xmlRoot.find('filename').text = str(file_name)
        for member in xmlRoot.findall('object'):
            member.find('name').text = member.find('name').text.lower()
        tree = ET.ElementTree(xmlRoot)
        tree.write(xml_path)


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
        new_name = file.with_suffix('.jpg')
        rgb_im.save(new_name)
        os.remove(origFile)
        updateXml(new_name)


# Renaming JPEG files:
jpeg_file_list = [path for path in Path(image_path).rglob('*.jpeg')]
num_files = len(jpeg_file_list)
if (num_files == 0):
    print('No JPEG images found in folder.')
else:
    print('Renaming ' + str(num_files) + ' JPEG images...')

    for file in jpeg_file_list:
        new_name = file.with_suffix('.jpg')
        file.rename(new_name)
        updateXml(new_name)


print('Complete.')
