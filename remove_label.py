"""
Beschreibung:
Dieses Skript entfernt spezifische Klassenlabels aus XML-Annotationsdateien (im Pascal VOC-Format) innerhalb eines angegebenen Verzeichnisses. 
Nur das angegebene Label wird entfernt, andere Labels bleiben unverändert. Falls keine Labels mehr vorhanden sind, wird die XML-Datei komplett gelöscht.

Funktionsweise:
1. Das Skript durchsucht ein angegebenes Verzeichnis (oder das aktuelle Arbeitsverzeichnis) rekursiv nach XML-Dateien.
2. In jeder gefundenen XML-Datei werden alle Objekte mit dem angegebenen Klassenlabel entfernt.
3. Falls nach der Entfernung keine Objekte mehr vorhanden sind, wird die gesamte XML-Datei gelöscht.
4. Andernfalls wird die aktualisierte XML-Datei gespeichert.

Verwendung:
1. Stelle sicher, dass Python 3.x installiert ist.
2. Führe das Skript mit den erforderlichen Argumenten aus:
   - `-p` oder `--path`: (Optional) Pfad zum Verzeichnis mit XML-Annotationsdateien. Standardmäßig wird das aktuelle Verzeichnis verwendet.
   - `-l` oder `--label`: (Erforderlich) Das Klassenlabel, das aus allen XML-Dateien entfernt werden soll.
   Beispiel: python remove_label.py -p "/pfad/zum/verzeichnis" -l label_to_remove

Ausgabe:
- Gibt die Anzahl der verarbeiteten XML-Dateien aus.
- Gibt die Anzahl der entfernten Objekte aus.
- Gibt die Anzahl der gelöschten XML-Dateien aus.
- Bestätigt den Abschluss der Verarbeitung.

Hinweise:
- Das zu entfernende Label wird in Kleinbuchstaben umgewandelt für den Vergleich.
- Es werden nur XML-Dateien im Pascal VOC-Format bearbeitet.
- Leere XML-Dateien (ohne Objekte) werden automatisch gelöscht.

Abhängigkeiten:
- Python 3.x
- xml.etree.ElementTree (In Python integriert)

"""


import os
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def remove_label_from_xml(xml_file_name, label_to_remove):
    """
    Entfernt alle Objekte mit dem angegebenen Label aus der XML-Datei.
    Löscht die Datei, falls keine Objekte mehr vorhanden sind.
    
    Returns:
        tuple: (objects_removed_count, file_deleted_bool)
    """
    if not os.path.isfile(xml_file_name):
        return 0, False
    
    try:
        tree = ET.parse(xml_file_name)
        xmlRoot = tree.getroot()
        
        objects_removed = 0
        objects_to_remove = []
        
        # Finde alle Objekte mit dem zu entfernenden Label
        for obj in xmlRoot.findall('object'):
            name_element = obj.find('name')
            if name_element is not None and name_element.text is not None:
                if name_element.text.lower() == label_to_remove:
                    objects_to_remove.append(obj)
                    objects_removed += 1
        
        # Entferne die gefundenen Objekte
        for obj in objects_to_remove:
            xmlRoot.remove(obj)
        
        # Prüfe, ob noch Objekte vorhanden sind
        remaining_objects = xmlRoot.findall('object')
        
        if len(remaining_objects) == 0:
            # Keine Objekte mehr vorhanden -> Datei löschen
            os.remove(xml_file_name)
            return objects_removed, True
        else:
            # Objekte vorhanden -> aktualisierte XML-Datei speichern
            tree.write(xml_file_name, encoding='utf-8', xml_declaration=True)
            return objects_removed, False
            
    except ET.ParseError as e:
        print(f"Error while parsing XML file {xml_file_name}: {e}")
        return 0, False
    except Exception as e:
        print(f"Error while processing XML file {xml_file_name}: {e}")
        return 0, False


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
    dest='label_to_remove',
    help='The class label to be removed from all images',
    required=True
)


args = parser.parse_args()

image_path = args.dataset_path
if (image_path is None or image_path == '.'):
    image_path = os.getcwd()

label_to_remove = args.label_to_remove
if (label_to_remove is None or label_to_remove.strip() == ''):
    print('Class label to remove must be given! Use argument -l LABEL_TO_REMOVE for label name to be removed from all images.')
else:
    label_to_remove = label_to_remove.lower()
    print('Folder: ' + image_path + ', label to remove: \"' + label_to_remove + '\"')
    files_processed = 0
    total_objects_removed = 0
    files_deleted = 0
    annotation_files_list = [path for path in Path(image_path).rglob('*.xml')]
    num_files = len(annotation_files_list)
    if (num_files == 0):
        print('No XML annotation files found in folder.')
    else:
        print(f'Processing {num_files} XML annotation files...')
        for xml_file in annotation_files_list:
            objects_removed, file_deleted = remove_label_from_xml(xml_file, label_to_remove)
            if objects_removed > 0 or file_deleted:
                files_processed += 1
                total_objects_removed += objects_removed
                if file_deleted:
                    files_deleted += 1
        if files_processed == 0:
            print('No objects with the specified label were found in any XML files.')
        else:
            print(f'{files_processed} XML files processed, {total_objects_removed} objects removed, {files_deleted} files deleted.')
    print('Conversion complete.')
