"""
Beschreibung:
Dieses Skript benennt Bilddateien in einem Verzeichnis rekursiv um, indem es jedem Bild einen zufälligen eindeutigen Dateinamen (UUID) zuweist. 
Falls zu einer Bilddatei eine XML-Annotationsdatei im Pascal VOC-Format existiert, wird diese aktualisiert, um den neuen Bilddateinamen und -pfad widerzuspiegeln.

Funktionsweise:
1. Das Skript durchsucht ein angegebenes Verzeichnis (standardmäßig das aktuelle Arbeitsverzeichnis) rekursiv nach Bilddateien in unterstützten Formaten (JPEG, PNG, JPG).
2. Jede gefundene Bilddatei wird in dasselbe Verzeichnis mit einem zufälligen UUID-basierten Dateinamen umbenannt.
3. Falls eine XML-Datei mit gleichem Namen wie die ursprüngliche Bilddatei existiert:
   - Wird der Bildname und -pfad in der XML-Datei entsprechend aktualisiert.
   - Die XML-Datei selbst wird ebenfalls umbenannt, sodass sie den neuen Bildnamen widerspiegelt.

Verwendung:
1. Stelle sicher, dass die benötigten Bibliotheken installiert sind (z. B. `xml.etree.ElementTree` ist in Python integriert).
2. Platziere die Bild- und XML-Dateien in einem Ordner.
3. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     python rename_images_and_update_xml.py /pfad/zum/verzeichnis

Ausgabe:
- Die Bilddateien werden umbenannt, und ihre zugehörigen XML-Dateien werden aktualisiert.
- Am Ende wird die Anzahl der umbenannten Bilder ausgegeben.

Hinweise:
- Das Skript verarbeitet nur Bilddateien mit den Formaten `.jpeg`, `.jpg`, `.png` (Groß-/Kleinschreibung wird berücksichtigt).
- Es prüft, ob ein neuer Dateiname bereits existiert, bevor er verwendet wird, um Konflikte zu vermeiden.

Abhängigkeiten:
- Python 3.x
- uuid (In Python integriert)

"""


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
