"""
Beschreibung:
Dieses Skript aktualisiert die Klassenlabels in XML-Annotationsdateien (im Pascal VOC-Format) innerhalb eines angegebenen Verzeichnisses. 
Alle vorhandenen Klassenlabels in den XML-Dateien werden durch das neue Label ersetzt.

Funktionsweise:
1. Das Skript durchsucht ein angegebenes Verzeichnis (oder das aktuelle Arbeitsverzeichnis) rekursiv nach XML-Dateien.
2. In jeder gefundenen XML-Datei werden alle Klassenlabels auf den angegebenen neuen Wert gesetzt.
3. Die XML-Dateien werden nach der Aktualisierung gespeichert.

Verwendung:
1. Stelle sicher, dass Python 3.x installiert ist.
2. Führe das Skript mit den erforderlichen Argumenten aus:
   - `-p` oder `--path`: (Optional) Pfad zum Verzeichnis mit XML-Annotationsdateien. Standardmäßig wird das aktuelle Verzeichnis verwendet.
   - `-l` oder `--label`: (Erforderlich) Das neue Klassenlabel, das in allen XML-Dateien verwendet werden soll.
   Beispiel: python update_xml_labels.py -p "/pfad/zum/verzeichnis" -l new_class_label

Ausgabe:
- Gibt die Anzahl der verarbeiteten XML-Dateien aus.
- Bestätigt den Abschluss der Aktualisierung.

Hinweise:
- Das neue Label wird in Kleinbuchstaben umgewandelt.
- Es werden nur XML-Dateien im Pascal VOC-Format bearbeitet.

Abhängigkeiten:
- Python 3.x
- xml.etree.ElementTree (In Python integriert)

"""


import os
import argparse
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
if (new_label is None or new_label.strip() == ''):
    print('New class label must be given! Use argument -l NEW_LABEL for new label name.')
else:
    new_label = new_label.lower()
    print('Folder: ' + image_path + ', new label: \"' + new_label + '\"')
    annotation_files_list = [path for path in Path(image_path).rglob('*.xml')]
    num_files = len(annotation_files_list)
    if (num_files == 0):
        print('No XML annotation files found in folder.')
    else:
        print(f'Processing {num_files} XML annotation files...')

        for file in annotation_files_list:
            updateXml(file, new_label)
    print('Conversion complete.')
