from sys import argv
import os
from pathlib import Path
from PIL import Image
import imagehash


IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')


def compare(image1_path, image2_path):
    with Image.open(image1_path) as img1:
        hashing1 = imagehash.phash(img1)
    with Image.open(image2_path) as img2:
        hashing2 = imagehash.phash(img2)
    return (hashing1 - hashing2) == 0


def selectWhichOneToRemove(image1_path, image2_path):
    file1 = Path(image1_path)
    folder1 = file1.parent
    filename1 = file1.stem
    xmlpath1 = os.path.join(folder1, filename1 + '.xml')
    if os.path.isfile(xmlpath1):
        return image2_path
    else:
        return image1_path
    

def remove(image_file_path):
    file = Path(image_file_path)
    folder = file.parent
    filename = file.stem
    xml_file_path = os.path.join(folder, filename + '.xml')
    if os.path.isfile(xml_file_path):
        os.remove(xml_file_path)
    os.remove(image_file_path)
    print('Deleting file: ' + image_file_path)



image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)


IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

images = []
for root, _, files in os.walk(image_path):
    for file in files:
        if file.endswith(IMAGE_FORMATS):
            file_path = os.path.join(root, file)
            images.append(file_path)

deleteCounter = 0
for img1 in images:
    for img2 in images:
        if (img1 is not img2 and os.path.isfile(img1) and os.path.isfile(img2)):
            if (compare(img1, img2)):
                remove(selectWhichOneToRemove(img1, img2))
                deleteCounter += 1

print(f'Detecting identical duplicates complete. {deleteCounter} images were removed.')
