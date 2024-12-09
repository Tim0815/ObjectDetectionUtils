"""
Beschreibung:
Dieses Skript gruppiert XML-Annotationsdateien (im Pascal VOC-Format) und zugehörige Bilddateien nach den in den Annotationen enthaltenen Klassen. 
Die Dateien werden in Verzeichnisse verschoben, die nach den Klassennamen benannt sind.

Funktionsweise:
1. Das Skript durchsucht ein angegebenes Verzeichnis (standardmäßig das aktuelle Arbeitsverzeichnis) nach XML-Annotationsdateien.
2. Jede XML-Datei wird analysiert, um die enthaltenen Klassen zu bestimmen.
3. Falls eine Datei nur eine Klasse enthält, werden die XML-Datei und die zugehörige Bilddatei in ein neues Unterverzeichnis verschoben, 
   das nach der Klasse benannt ist.
4. Die XML-Datei wird entsprechend aktualisiert, um den neuen Speicherort der Bilddatei zu reflektieren.
5. Dateien mit mehreren Klassen werden übersprungen, und eine Meldung wird ausgegeben.

Verwendung:
1. Stelle sicher, dass die benötigten Bibliotheken installiert sind (z. B. `xml.etree.ElementTree` ist in Python integriert).
2. Platziere die XML-Dateien und die zugehörigen Bilder in einem Ordner.
3. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     python group_files_per_class.py /pfad/zum/verzeichnis

Ausgabe:
- Die Dateien werden in nach Klassen benannte Unterverzeichnisse verschoben.
- Am Ende wird die Anzahl der gruppierten Dateien und die Liste der gefundenen Klassen ausgegeben.

Hinweise:
- Das Skript verarbeitet nur Dateien mit genau einer Klasse pro Annotation.
- Mehrklassen-Annotationen werden ignoriert, und eine entsprechende Warnung wird ausgegeben.

Abhängigkeiten:
- Python 3.x

"""


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
