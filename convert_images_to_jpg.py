from sys import argv
from pathlib import Path
from PIL import Image
import os

image_path = argv[1]

png_file_list = [path for path in Path(image_path).rglob('*.png')]
for file in png_file_list:
    origFile = file
    im = Image.open(file)
    rgb_im = im.convert('RGB')
    rgb_im.save(file.with_suffix('.jpg'))
    os.remove(origFile)
