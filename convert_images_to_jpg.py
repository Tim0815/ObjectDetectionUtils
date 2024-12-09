"""
Beschreibung:
Dieses Skript konvertiert PNG-Bilder in JPG-Format und benennt JPEG-Bilder in JPG um. 
Es sucht in einem angegebenen Verzeichnis (oder im aktuellen Verzeichnis) nach PNG- und JPEG-Bildern und führt die Konvertierung sowie Umbenennung durch.
Zusätzlich wird die zugehörige XML-Annotationsdatei im Pascal VOC-Format angepasst, um den neuen Dateinamen und Pfad widerzuspiegeln.

Funktionsweise:
1. Das Skript durchsucht das angegebene Verzeichnis (oder das aktuelle Arbeitsverzeichnis) nach PNG- und JPEG-Dateien.
2. PNG-Bilder werden in das JPG-Format konvertiert, und die Originaldateien werden gelöscht.
3. JPEG-Bilder werden von `.jpeg` auf `.jpg` umbenannt.
4. Jede betroffene XML-Datei im Pascal VOC-Format wird aktualisiert, um den neuen Bildnamen und Pfad widerzuspiegeln.
5. Alle Klassennamen in den XML-Dateien werden in Kleinbuchstaben umgewandelt.

Verwendung:
1. Stelle sicher, dass die benötigten Bibliotheken installiert sind (z. B. Pillow für die Bildverarbeitung).
2. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     ```bash
     python convert_and_rename_images.py /pfad/zum/verzeichnis
     ```
3. Ausgabe:
   - Konvertiert alle PNG-Bilder in JPG und benennt JPEG-Bilder um.
   - Aktualisiert die zugehörigen XML-Dateien, um den neuen Dateinamen und Pfad widerzuspiegeln.

Hinweise:
- Es werden nur PNG- und JPEG-Bilder verarbeitet.
- Falls eine XML-Datei existiert, wird sie aktualisiert, um den neuen Dateinamen und Pfad widerzuspiegeln.
- Klassennamen in den XML-Dateien werden in Kleinbuchstaben konvertiert.

Abhängigkeiten:
- Python 3.x
- Pillow (Installierbar via `pip install pillow`)
- xml.etree.ElementTree (In Python integriert)
- uuid (In Python integriert)

"""


from sys import argv
from pathlib import Path
from PIL import Image
import os
import xml.etree.ElementTree as ET
import uuid


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
        xmlRoot.find('filename').text = str(fn + '.jpg')
        xmlRoot.find('path').text = str(file_name)
        for member in xmlRoot.findall('object'):
            member.find('name').text = member.find('name').text.lower()
        tree = ET.ElementTree(xmlRoot)
        tree.write(xml_path)


# Converting PNG files:
png_file_list = [path for path in Path(image_path).rglob('*.png')]
num_files = len(png_file_list)
if (num_files == 0):
    print('No PNG images found in folder.')
else:
    print('Converting ' + str(num_files) + ' PNG images...')

    for file in png_file_list:
        try:
            origFile = file
            im = Image.open(file)
            rgb_im = im.convert('RGB')
            new_name = file.with_suffix('.jpg')
            while new_name.exists():
                new_name = new_name.with_stem(str(uuid.uuid4().hex))
            rgb_im.save(new_name)
            os.remove(origFile)
            updateXml(new_name)
        except:
            print(f'Error with file {file}')


# Renaming JPEG files:
jpeg_file_list = [path for path in Path(image_path).rglob('*.jpeg')]
num_files = len(jpeg_file_list)
if (num_files == 0):
    print('No JPEG images found in folder.')
else:
    print('Renaming ' + str(num_files) + ' JPEG images...')

    for file in jpeg_file_list:
        new_name = file.with_suffix('.jpg')
        while new_name.exists():
            new_name = new_name.with_stem(str(uuid.uuid4().hex))
        file.rename(new_name)
        updateXml(new_name)


print('Complete.')
