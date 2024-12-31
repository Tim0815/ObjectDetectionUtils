"""
Beschreibung:
Dieses Skript konvertiert PNG-Bilder in JPG-Format und benennt JPEG-Bilder in JPG um. 
Es sucht in einem angegebenen Verzeichnis (oder im aktuellen Verzeichnis) nach PNG- und JPEG-Bildern und führt die Konvertierung sowie Umbenennung durch.
Zusätzlich wird die zugehörige XML-Annotationsdatei im Pascal VOC-Format angepasst, um den neuen Dateinamen und Pfad widerzuspiegeln.

Funktionsweise:
1. Das Skript durchsucht das angegebene Verzeichnis (oder das aktuelle Arbeitsverzeichnis) nach PNG-, WEBP-, AVIF- und JPEG-Dateien.
2. PNG-, WEBP- und AVIF-Bilder werden in das JPG-Format konvertiert, und die Originaldateien werden gelöscht.
3. JPEG-Bilder werden von `.jpeg` auf `.jpg` umbenannt.
4. Jede betroffene XML-Datei im Pascal VOC-Format wird aktualisiert, um den neuen Bildnamen und Pfad widerzuspiegeln.
5. Außerdem werden alle Klassennamen in den XML-Dateien in Kleinbuchstaben umgewandelt.

Verwendung:
1. Stelle sicher, dass die benötigten Bibliotheken installiert sind (z. B. Pillow für die Bildverarbeitung).
2. Führe das Skript aus:
   - Ohne Argument: Das Skript arbeitet im aktuellen Verzeichnis.
   - Mit Argument: Übergib das Zielverzeichnis als Parameter. Beispiel:
     ```bash
     python convert_and_rename_images.py /pfad/zum/verzeichnis
     ```
3. Ausgabe:
   - Konvertiert alle PNG-, WEBP- und AVIF-Bilder in JPG und benennt JPEG-Bilder um.
   - Aktualisiert die zugehörigen XML-Dateien, um den neuen Dateinamen und Pfad widerzuspiegeln.

Hinweise:
- Es werden PNG-, WEBP-, AVIF- und JPEG-Bilder verarbeitet.
- Falls eine XML-Datei existiert, wird sie aktualisiert, um den neuen Dateinamen und Pfad widerzuspiegeln.
- Klassennamen in den XML-Dateien werden in Kleinbuchstaben konvertiert.

Abhängigkeiten:
- Python 3.x
- Pillow (Installierbar via `pip install pillow`)
- pillow_avif
- pillow_heif (für das WEBP-Format)
- xml.etree.ElementTree (In Python integriert)
- uuid (In Python integriert)

"""


from sys import argv
from pathlib import Path
import pillow_avif
from pillow_heif import register_heif_opener
from PIL import Image
import os
import xml.etree.ElementTree as ET
import uuid


image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)

register_heif_opener()


# Update XML file if it exists:
def updateXml(origImgFile, newImgFile):
    origXmlFile = origImgFile.with_suffix('.xml')
    if origXmlFile.exists():
        xmlRoot = ET.parse(origXmlFile).getroot()
        xmlRoot.find('filename').text = str(newImgFile.name)
        xmlRoot.find('path').text = str(newImgFile)
        for member in xmlRoot.findall('object'):
            member.find('name').text = member.find('name').text.lower()

        newXmlFile = newImgFile.with_suffix('.xml')
        tree = ET.ElementTree(xmlRoot)
        tree.write(newXmlFile)
        if (origXmlFile != newXmlFile):
            os.remove(origXmlFile)


# Converting files:
def convert(imagePath, ext):
    fileList = [path for path in Path(imagePath).rglob(f"*.{ext}")]
    numFiles = len(fileList)
    if (numFiles == 0):
        print(f"No {ext} images found in folder.")
    else:
        print(f"Converting {str(numFiles)} {ext} images...")

        for file in fileList:
            try:
                im = Image.open(file)
                if not im.mode == 'RGB':
                    im = im.convert('RGB')
                new_name = file.with_suffix('.jpg')
                while new_name.exists():
                    new_name = new_name.with_stem(str(uuid.uuid4().hex))
                im.save(new_name)
                os.remove(file)
                updateXml(file, new_name)
            except Exception as e:
                print(f"Error with file {file} =>", e)


convert(image_path, 'png')
convert(image_path, 'webp')
convert(image_path, 'avif')


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
        updateXml(file, new_name)


print('Complete.')
