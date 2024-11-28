import os
import argparse
from optparse import OptionParser
import cv2
import numpy as np
import xml.etree.ElementTree as ET
from math import floor
from pathlib import Path
from PIL import Image


def create_path(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)


def get_file_name(path):
    base_dir = os.path.dirname(path)
    file_name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.replace(".", "")
    return (base_dir, file_name, ext)


def process_image(file_path, output_path, x, y, save_box_images, mode):
    (base_dir, file_name, ext) = get_file_name(file_path)
    # image_path = os.path.join(base_dir, file_name + '.' + ext)
    xml = os.path.join(base_dir, file_name + '.xml')
    try:
        resize(
            file_path,
            xml,
            (x, y),
            output_path,
            mode,
            save_box_images=save_box_images
        )
    except Exception as e:
        print('[ERROR] error with {}\n file: {}'.format(file_path, e))
        print('--------------------------------------------------')


def draw_box(boxes, image, path):
    for i in range(0, len(boxes)):
        cv2.rectangle(image, (boxes[i][2], boxes[i][3]), (boxes[i][4], boxes[i][5]), (255, 0, 0), 1)
    cv2.imwrite(path, image)


def resize(image_path,
           xml_path,
           newSize,
           output_path,
           mode,
           save_box_images=False,
           verbose=False
           ):

    (base_dir, file_name, ext) = get_file_name(image_path)
    image = cv2.imread(image_path)
    imgW = float(image.shape[1])
    imgH = float(image.shape[0])
    newW = float(newSize[0])
    newH = float(newSize[1])
    scale_x = newW / imgW
    scale_y = newH / imgH

    mode = mode and mode.lower()
    # Standard resize mode
    if mode is None or mode == 'size':
        newSize = (int(newSize[0]), int(newSize[1]))
        image = cv2.resize(src=image, dsize=(newSize[0], newSize[1]))
    else:
        # Scaling by factor or percentage of the original image size
        if mode == 'scale':
            if scale_y > scale_x:
                scale_x = scale_y
            else:
                scale_y = scale_x
            interp = cv2.INTER_LINEAR if (scale_x > 1.0) else cv2.INTER_AREA
            image = cv2.resize(
                src=image,
                dsize=(0, 0), dst=None,
                fx=scale_x, fy=scale_y, interpolation=interp)
        # Target mode; choose the correct ratio to reach one of the x/y targets without oversize
        elif mode == 'target':
            if scale_y < scale_x:
                scale_x = scale_y
            else:
                scale_y = scale_x
            interp = cv2.INTER_LINEAR if (scale_x > 1.0) else cv2.INTER_AREA
            image = cv2.resize(
                src=image,
                dsize=(0, 0), dst=None,
                fx=scale_x, fy=scale_y, interpolation=interp)
        else:
            raise Exception(f"Invalid resize mode: {mode}")

    newBoxes = []
    xmlRoot = ET.parse(xml_path).getroot()
    xmlRoot.find('filename').text = str(file_name + '.' + ext)
    size_node = xmlRoot.find('size')
    size_node.find('width').text = str(newSize[0])
    size_node.find('height').text = str(newSize[1])

    for member in xmlRoot.findall('object'):
        member.find('name').text = member.find('name').text.lower()
        bndbox = member.find('bndbox')

        xmin = bndbox.find('xmin')
        ymin = bndbox.find('ymin')
        xmax = bndbox.find('xmax')
        ymax = bndbox.find('ymax')
        
        xmin.text = str(int(np.round(float(xmin.text) * scale_x)))
        ymin.text = str(int(np.round(float(ymin.text) * scale_y)))
        xmax.text = str(int(np.round(float(xmax.text) * scale_x)))
        ymax.text = str(int(np.round(float(ymax.text) * scale_y)))

        newBoxes.append([
            1,
            0,
            int(float(xmin.text)),
            int(float(ymin.text)),
            int(float(xmax.text)),
            int(float(ymax.text))
            ])

    new_img_file_name = os.path.join(output_path, file_name + '.' + ext)
    cv2.imwrite(new_img_file_name, image)

    tree = ET.ElementTree(xmlRoot)
    tree.write(os.path.join(output_path, file_name + '.xml'))
    if int(save_box_images):
        save_path = '{}\\boxes_images\\boxed_{}'.format(output_path, ''.join([file_name, '.', ext]))
        draw_box(newBoxes, image, save_path)




IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

def resize_all(inPath, outPath, x, y, save_box_images = 0, mode = 'size'):
    create_path(outPath)
    if int(save_box_images):
        create_path(os.path.join(outPath, 'boxes_images'))

    for root, _, files in os.walk(inPath):
            out_path = outPath + root[len(inPath):]
            create_path(out_path)

            for file in files:
                if file.endswith(IMAGE_FORMATS):
                    file_path = os.path.join(root, file)
                    process_image(file_path, out_path, x, y, save_box_images, mode)
    print('Complete.')




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
    '-o',
    '--output',
    dest='output_path',
    help='Path that will be saved the resized dataset',
    default='.',
    required=False
)
parser.add_argument(
    '-x',
    '--new_x',
    dest='x',
    help='The new x images size',
    default=320,
    required=False
)
parser.add_argument(
    '-y',
    '--new_y',
    dest='y',
    help='The new y images size',
    default=320,
    required=False
)
parser.add_argument(
    '-m',
    '--mode',
    dest='mode',
    help='Resize mode: size, scale, or target',
    required=False
)
parser.add_argument(
    '-s',
    '--save_box_images',
    dest='save_box_images',
    help='If True, it will save the resized image and a drawed image with the boxes in the images',
    default=0
)



args = parser.parse_args()

input_path = args.dataset_path
output_path = args.output_path

if input_path is None or input_path == '.':
    input_path = os.getcwd()

if output_path is None or output_path == '.':
    output_path = input_path

resize_all(input_path, output_path, args.x, args.y, args.save_box_images, args.mode)
