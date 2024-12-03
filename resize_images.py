import os
import argparse
from optparse import OptionParser
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import copy
from math import floor
from pathlib import Path
from PIL import Image


def create_path(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)


def clamp(number, _min, _max):
    return max(_min, min(_max, number))


def get_file_name(path):
    base_dir = os.path.dirname(path)
    file_name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.replace(".", "")
    return (base_dir, file_name, ext)


def process_image(file_path, output_path, x, y, mode):
    (base_dir, file_name, ext) = get_file_name(file_path)
    # image_path = os.path.join(base_dir, file_name + '.' + ext)
    xml = os.path.join(base_dir, file_name + '.xml')
    try:
        resize(file_path, xml, (x, y), output_path, mode)
    except Exception as e:
        print('[ERROR] error with {}\n file: {}'.format(file_path, e))
        print('--------------------------------------------------')


def resize(image_path, xml_path, newSize, output_path, mode):
    (base_dir, file_name, ext) = get_file_name(image_path)
    image = cv2.imread(image_path)
    xmlRoot = ET.parse(xml_path).getroot()

    imgW = float(image.shape[1])
    imgH = float(image.shape[0])
    newW = float(newSize[0])
    newH = float(newSize[1])
    scaleX = newW / imgW
    scaleY = newH / imgH

    mode = mode and mode.lower()
    # Standard resize mode
    if mode is None or mode == 'size':
        resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
    else:
        # Scaling mode: choose the correct scale to reach one of the x/y targets without undersize
        if mode == 'scale':
            if scaleY > scaleX:
                scaleX = scaleY
                newW = scaleX * imgW
            else:
                scaleY = scaleX
                newH = scaleY * imgH
            resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
        # Target mode: choose the correct scale to reach one of the x/y targets without oversize
        elif mode == 'target':
            if scaleY < scaleX:
                scaleX = scaleY
                newW = scaleX * imgW
            else:
                scaleY = scaleX
                newH = scaleY * imgH
            resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
        # Crop mode: first, scale down to reach larger x/y edge size without undersize, afterwards check if crop is needed and split the image into parts
        elif mode == 'crop':
            if scaleY > scaleX:
                scaleX = scaleY
                tX = int(scaleX * imgW - newW)
                resize_and_save_internal(image, xmlRoot, file_name + '_1', ext, int(newW), int(newH), scaleX, scaleY, tX, 0, output_path)
                resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
            elif scaleX > scaleY:
                scaleY = scaleX
                tY = int(scaleY * imgH - newH)
                resize_and_save_internal(image, xmlRoot, file_name + '_1', ext, int(newW), int(newH), scaleX, scaleY, 0, tY, output_path)
                resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
            else:
                resize_and_save_internal(image, xmlRoot, file_name, ext, int(newW), int(newH), scaleX, scaleY, 0, 0, output_path)
        else:
            raise Exception(f"Invalid resize mode: {mode}")


def resize_and_save_internal(image, origXmlRoot, file_name, ext, newW, newH, scaleX, scaleY, tX, tY, output_path):
    interp = cv2.INTER_LINEAR if (scaleX * scaleY > 1.0) else cv2.INTER_AREA
    image = cv2.resize(src=image, dsize=(0, 0), dst=None, fx=scaleX, fy=scaleY, interpolation=interp)
    # image = cv2.resize(src=image, dsize=(newW, newH))
    imgW = image.shape[1]
    imgH = image.shape[0]
    if (imgW != newW or tX > 0 or imgH != newH or tY > 0):
        image = image[tY:newH+tY, tX:newW+tX]

    xmlRoot = copy.deepcopy(origXmlRoot)
    xmlRoot.find('filename').text = str(file_name + '.' + ext)
    xmlRoot.find('path').text = str(output_path)

    size_node = xmlRoot.find('size')
    size_node.find('width').text = str(newW)
    size_node.find('height').text = str(newH)

    for xmlObject in xmlRoot.findall('object'):
        name = xmlObject.find('name')
        name.text = name.text.lower()

        bndbox = xmlObject.find('bndbox')
        xmin = bndbox.find('xmin')
        ymin = bndbox.find('ymin')
        xmax = bndbox.find('xmax')
        ymax = bndbox.find('ymax')
        
        xminFloat = float(xmin.text)
        yminFloat = float(ymin.text)
        xmaxFloat = float(xmax.text)
        ymaxFloat = float(ymax.text)

        xminInt = clamp(int(np.round(xminFloat * scaleX)) - tX, 0, newW)
        yminInt = clamp(int(np.round(yminFloat * scaleY)) - tY, 0, newH)
        xmaxInt = clamp(int(np.round(xmaxFloat * scaleX)) - tX, 0, newW)
        ymaxInt = clamp(int(np.round(ymaxFloat * scaleY)) - tY, 0, newH)
        
        if (xminInt == newW or xmaxInt == 0 or yminInt == newH or ymaxInt == 0):
            xmlRoot.remove(xmlObject)
        else:
            xmin.text = str(xminInt)
            ymin.text = str(yminInt)
            xmax.text = str(xmaxInt)
            ymax.text = str(ymaxInt)

    cv2.imwrite(os.path.join(output_path, file_name + '.' + ext), image)

    tree = ET.ElementTree(xmlRoot)
    tree.write(os.path.join(output_path, file_name + '.xml'))




IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

def resize_all(inPath, outPath, x, y, mode = 'size'):
    create_path(outPath)
    for root, _, files in os.walk(inPath):
            out_path = outPath + root[len(inPath):]
            create_path(out_path)

            for file in files:
                if file.endswith(IMAGE_FORMATS):
                    file_path = os.path.join(root, file)
                    process_image(file_path, out_path, x, y, mode)
    print('Complete.')




parser = argparse.ArgumentParser()

parser.add_argument(
    '-p',
    '--path',
    dest='dataset_path',
    help='Path to dataset (images and annotations)',
    default='.',
    required=False
)
parser.add_argument(
    '-o',
    '--output',
    dest='output_path',
    help='Output path for resized dataset (might be left empty, then the input will be overwritten)',
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
    help='Resize mode: size, scale, target, or crop',
    required=False
)



args = parser.parse_args()

input_path = args.dataset_path
output_path = args.output_path

if input_path is None or input_path == '.':
    input_path = os.getcwd()

if output_path is None or output_path == '.':
    output_path = input_path

resize_all(input_path, output_path, args.x, args.y, args.mode)
