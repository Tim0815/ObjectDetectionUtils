"""
Beschreibung:
Dieses Skript überprüft XML-Annotationsdateien (im Pascal VOC-Format) in einem Verzeichnis und führt folgende Aufgaben aus:
1. Es prüft, ob Klassennamen in Großbuchstaben vorliegen, und wandelt diese automatisch in Kleinbuchstaben um.
2. Es sammelt alle in den XML-Dateien gefundenen Klassen und gibt diese am Ende aus.
3. Aktualisierte XML-Dateien werden überschrieben.

Funktionsweise:
1. Das Skript durchsucht ein angegebenes Verzeichnis (oder das aktuelle Arbeitsverzeichnis) rekursiv nach XML-Dateien.
2. Jede XML-Datei wird analysiert:
   - Klassennamen in Großbuchstaben werden erkannt und in Kleinbuchstaben umgewandelt.
   - Alle gefundenen Klassen werden in einer Liste gespeichert.
3. Eine Warnung wird ausgegeben, wenn ein Großbuchstaben-Name korrigiert wird.

Verwendung:
1. Stelle sicher, dass Python 3.x installiert ist.
2. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     ```bash
     python check_and_update_xml_classes.py /pfad/zum/verzeichnis
     ```

Ausgabe:
- Gibt die Anzahl der überprüften XML-Dateien aus.
- Gibt die Anzahl der geänderten Dateien und die Liste der gefundenen Klassen aus.

Hinweise:
- Nur Klassennamen werden bearbeitet, die Großbuchstaben enthalten.
- Es werden ausschließlich XML-Dateien im Pascal VOC-Format berücksichtigt.

Abhängigkeiten:
- Python 3.x
- xml.etree.ElementTree (In Python integriert)

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
updates = 0


# Check XML file:
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


# Find and process all XML files:
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
