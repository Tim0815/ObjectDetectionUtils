from sys import argv
from pathlib import Path
import os
import xml.etree.ElementTree as ET


images_path = os.getcwd()
if (len(argv) >= 2):
    images_path = argv[1]
print('Folder: ' + images_path)


classes = []
groupingCounter = 0

# Group XML file:
def groupXml(xml_path):
    global classes, groupingCounter

    xmlRoot = ET.parse(xml_path).getroot()
    localClasses = []

    for member in xmlRoot.findall('object'):
        class_name = member.find('name').text.lower()
        if class_name not in localClasses:
            localClasses.append(class_name)

    n = len(localClasses)
    if (n == 1):
        className = str(localClasses[0]).lower()
        if className not in classes:
            classes.append(className)
        for member in xmlRoot.findall('object'):
            member.find('name').text = className
        xmlFile = Path(xml_path)
        currentFolder = xmlFile.parent
        currentFolderName = currentFolder.name
        if (currentFolderName != className):
            newFolderName = className.capitalize()
            newFolder = currentFolder.joinpath(newFolderName)
            newFolder.mkdir(parents=True, exist_ok=True)

            xmlRoot.find('folder').text = newFolderName
            imgFileName = xmlRoot.find('filename').text
            img_path = os.path.join(currentFolder, imgFileName)
            if os.path.isfile(img_path):
                xmlRoot.find('path').text = str(os.path.join(newFolder, imgFileName))
                tree = ET.ElementTree(xmlRoot)
                tree.write(xml_path)

                xmlFileName = xmlFile.stem + '.' + xmlFile.suffix.removeprefix('.')
                os.rename(xml_path, os.path.join(newFolder, xmlFileName))

                os.rename(img_path, os.path.join(newFolder, imgFileName))
                
                groupingCounter += 1
    else:
        print(f"Found {n} classes in {xml_path}: {str(localClasses)}")



# Find and process XML files:
xml_file_list = [path for path in Path(images_path).rglob('*.xml')]
num_files = len(xml_file_list)
if (num_files == 0):
    print("No XML annotation files found in folder.")
else:
    print(f"Trying to group {str(num_files)} XML annotation files...")

    for file in xml_file_list:
        try:
            groupXml(file)
        except:
            print(f"Error occured in file {file}!")

print(f"Check complete. {str(groupingCounter)} files were grouped. {str(len(classes))} classes found during conversion: \n{str(classes)}")
