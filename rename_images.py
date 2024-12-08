from sys import argv
import os
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET


def updateXml(xml_file_path, newFileNameWithExtension, newImageFilePath):
    xmlRoot = ET.parse(xml_file_path).getroot()
    xmlRoot.find('folder').text = 'XML'
    xmlRoot.find('filename').text = str(newFileNameWithExtension)
    xmlRoot.find('path').text = str(newImageFilePath)
    for member in xmlRoot.findall('object'):
        name = member.find('name')
        name.text = name.text.lower()
    tree = ET.ElementTree(xmlRoot)
    tree.write(xml_file_path)

def rename_image(image_file_path):
    file = Path(image_file_path)
    folder = file.parent
    filename = file.stem
    ext = file.suffix.removeprefix('.')
    newFileName = str(uuid.uuid4().hex)
    newFileNameWithExtension = newFileName + '.' + ext
    newImageFilePath = os.path.join(folder, newFileNameWithExtension)
    while os.path.exists(newImageFilePath):
        newFileName = str(uuid.uuid4().hex)
        newFileNameWithExtension = newFileName + '.' + ext
        newImageFilePath = os.path.join(folder, newFileNameWithExtension)
    os.rename(image_file_path, newImageFilePath)

    xml_file_path = os.path.join(folder, filename + '.xml')
    if os.path.isfile(xml_file_path):
        updateXml(xml_file_path, newFileNameWithExtension, newImageFilePath)
        newXmlFilePath = os.path.join(folder, newFileName + '.xml')
        os.rename(xml_file_path, newXmlFilePath)


image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)


IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

renameCounter = 0
for root, _, files in os.walk(image_path):
    for file in files:
        if file.endswith(IMAGE_FORMATS):
            file_path = os.path.join(root, file)
            rename_image(file_path)
            renameCounter += 1

print(f'Renaming complete. {renameCounter} images were renamed.')
