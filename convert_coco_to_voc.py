from sys import argv
from pathlib import Path
import os
from pycocotools.coco import COCO
from pascal_voc_writer import Writer


def coco2voc(annotations_file, output_dir):
    print(f'Starting conversion of {annotations_file}')

    # Erstelle das Ausgabe-Verzeichnis, falls es nicht existiert
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Lade die COCO-Annotationsdatei
    coco = COCO(annotations_file)

    # Count number of errors during conversion
    errors = 0
    results = 0

    print(f'Found {len(coco.getImgIds())} images in this annotation file.')

    # Hole die Bilder und Annotationen aus der COCO-JSON-Datei
    for image_id in coco.getImgIds():
        image_info = coco.loadImgs(image_id)[0]
        image_filename = image_info['file_name']
        image_width = image_info['width']
        image_height = image_info['height']

        # Erstelle den Pascal VOC Writer für das aktuelle Bild
        writer = Writer(image_filename, image_width, image_height)

        # Hole alle Annotationen für das aktuelle Bild
        annotation_ids = coco.getAnnIds(imgIds=image_id)
        annotations = coco.loadAnns(annotation_ids)

        # Füge die Annotationen in das Pascal VOC-Format ein
        num_boxes = 0
        for annotation in annotations:
            try:
                if 'bbox' in annotation:
                    category_id = annotation['category_id']
                    category_name = coco.loadCats(category_id)[0]['name']

                    # COCO verwendet bounding boxes im Format [x, y, width, height]
                    bbox = annotation['bbox']
                    x_min = int(bbox[0])
                    y_min = int(bbox[1])
                    x_max = int(bbox[0] + bbox[2])
                    y_max = int(bbox[1] + bbox[3])

                    # Füge die Annotation hinzu
                    writer.addObject(category_name, x_min, y_min, x_max, y_max)

                    # Count number of bounding boxes for this image
                    num_boxes += 1
            except:
                errors += 1

        if (num_boxes > 0):
            # Speichere die Pascal VOC-Datei
            output_file = os.path.join(output_dir, f"{Path(image_filename).stem}.xml")
            writer.save(str(output_file))
            results += 1

    print(f'Conversion of {annotations_file} completed. {results} images converted, {errors} errors occured.')


json_path = os.getcwd()
if (len(argv) >= 2):
    json_path = argv[1]
print('Folder: ' + json_path)


json_file_list = [path for path in Path(json_path).rglob('*.json')]
num_files = len(json_file_list)
if (num_files == 0):
    print('No JSON files found in folder.')

for json_file in json_file_list:
    coco2voc(json_file, Path(json_file).stem)

print('Conversion complete.')
