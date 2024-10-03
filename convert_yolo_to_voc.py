from sys import argv
from pathlib import Path
import os
import re
from PIL import Image


image_path = os.getcwd()
if (len(argv) >= 2):
    image_path = argv[1]
print('Folder: ' + image_path)


# Description of Yolo Format values
# Chicken 0.448743 0.529142 0.051587 0.021081
# class_name x_yolo y_yolo yolo_width yolo_height

def is_number(n):
    try:
        float(n)
        return True
    except ValueError:
        return False

txt_file_list = [path for path in Path(image_path).rglob('*.txt')]
num_files = len(txt_file_list)
if (num_files == 0):
    print('No TXT files found in folder.')
else:
    print('Converting ' + str(num_files) + ' files...')


classes = []

for txt_file in txt_file_list:
    the_file = open(txt_file, 'r')
    all_lines = the_file.readlines()
    # print('Converting file ' + str(the_file.name))
    image_name = txt_file.stem
    image_dir = txt_file.parent.parent
    xml_file = os.path.join(image_dir, image_name + '.xml')

    # Check to see if there is an image that matches the txt file
    if os.path.isfile(os.path.join(image_dir, image_name + '.jpeg')):
        image_name = image_name + '.jpeg'
    if os.path.isfile(os.path.join(image_dir, image_name + '.jpg')):
        image_name = image_name + '.jpg'
    if os.path.isfile(os.path.join(image_dir, image_name + '.png')):
        image_name = image_name + '.png'
    if os.path.isfile(os.path.join(image_dir, image_name + '.bmp')):
        image_name = image_name + '.bmp'

    if not image_name == txt_file.stem:
        # print('  > Image file found: ' + str(os.path.join(image_dir, image_name)))

        # If the image name is the same as the yolo filename
        # then we did NOT find an image that matches, and we will skip this code block
        orig_img = Image.open(os.path.join(image_dir, image_name)) # open the image
        image_width = orig_img.width
        image_height = orig_img.height

        # Start the XML file
        # print('  > Creating XML file: ' + xml_file)
        with open(xml_file, 'w') as f:
          f.write('<annotation>\n')
          f.write('\t<folder>XML</folder>\n')
          f.write('\t<filename>' + image_name + '</filename>\n')
          f.write('\t<path>' + str(os.path.join(image_dir, image_name)) + '</path>\n')
          f.write('\t<source>\n')
          f.write('\t\t<database>Unknown</database>\n')
          f.write('\t</source>\n')
          f.write('\t<size>\n')
          f.write('\t\t<width>' + str(image_width) + '</width>\n')
          f.write('\t\t<height>' + str(image_height) + '</height>\n')
          f.write('\t\t<depth>3</depth>\n') # assuming a 3 channel color image (RGB)
          f.write('\t</size>\n')
          f.write('\t<segmented>0</segmented>\n')
        
          for each_line in all_lines:
              # regex to find the numbers in each line of the text file
              yolo_array = re.split("\s", each_line.rstrip()) # remove any extra space from the end of the line

              # initalize the variables
              x_yolo = 0.0
              y_yolo = 0.0
              yolo_width = 0.0
              yolo_height = 0.0
              yolo_array_contains_only_digits = True

              # make sure the array has the correct number of items
              if len(yolo_array) == 5:
                  # assign the variables
                  object_name = yolo_array[0].lower()
                  x_yolo = float(yolo_array[1])
                  y_yolo = float(yolo_array[2])
                  yolo_width = float(yolo_array[3])
                  yolo_height = float(yolo_array[4])

                  # Convert Yolo Format to Pascal VOC format
                  # box_width = yolo_width * image_width
                  # box_height = yolo_height * image_height
                  # x_min = str(int(x_yolo * image_width - (box_width / 2)))
                  # y_min = str(int(y_yolo * image_height - (box_height / 2)))
                  # x_max = str(int(x_yolo * image_width + (box_width / 2)))
                  # y_max = str(int(y_yolo * image_height + (box_height / 2)))
                  x_min = str(round(x_yolo))
                  y_min = str(round(y_yolo))
                  x_max = str(round(yolo_width))
                  y_max = str(round(yolo_height))

                  # write each object to the file
                  f.write('\t<object>\n')
                  f.write('\t\t<name>' + object_name + '</name>\n')
                  f.write('\t\t<pose>Unspecified</pose>\n')
                  f.write('\t\t<truncated>0</truncated>\n')
                  f.write('\t\t<difficult>0</difficult>\n')
                  f.write('\t\t<bndbox>\n')
                  f.write('\t\t\t<xmin>' + x_min + '</xmin>\n')
                  f.write('\t\t\t<ymin>' + y_min + '</ymin>\n')
                  f.write('\t\t\t<xmax>' + x_max + '</xmax>\n')
                  f.write('\t\t\t<ymax>' + y_max + '</ymax>\n')
                  f.write('\t\t</bndbox>\n')
                  f.write('\t</object>\n')
                  
                  if object_name not in classes:
                      classes.append(object_name)

          # Close the annotation tag once all the objects have been written to the file
          f.write('</annotation>\n')
          f.close() # Close the file

print('Conversion complete. ' + str(len(classes)) + ' classes found during conversion: ' + str(classes))
