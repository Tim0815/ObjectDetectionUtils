from sys import argv
from pathlib import Path
import os
import xml.etree.ElementTree as ET


images_path = os.getcwd()
if (len(argv) >= 2):
    images_path = argv[1]
print('Folder: ' + images_path)


classes = []
updates = 0


# Check XML file if it exists:
def checkXml(xml_path):
    global updates
    xmlRoot = ET.parse(xml_path).getroot()
    for member in xmlRoot.findall('object'):
        object_name = member.find('name').text
        if not object_name.islower():
            print('WARNING: Uppercase class name found in ' + str(xml_path.name) + ' --> ' + object_name)
            object_name = object_name.lower()
            member.find('name').text = object_name
            tree = ET.ElementTree(xmlRoot)
            tree.write(xml_path)
            updates += 1

        if object_name not in classes:
            classes.append(object_name)


# Converting PNG files:
xml_file_list = [path for path in Path(images_path).rglob('*.xml')]
num_files = len(xml_file_list)
if (num_files == 0):
    print('No XML annotation files found in folder.')
else:
    print('Checking ' + str(num_files) + ' XML annotation files...')

    for file in xml_file_list:
        checkXml(file)


result = 'Check complete. '
if updates > 0:
    result = result + str(updates) + ' XML files were updated. '
result = result + str(len(classes)) + ' classes found during conversion: \n' + str(classes)
print(result)
