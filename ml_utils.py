import sys, platform, os, subprocess, copy, time, random, shutil, cv2
from pathlib import Path
import xml.etree.ElementTree as ET
from math import floor
import numpy as np
from PIL import Image



# This script resizes the given annotated images as best as possible.
# Instead of resizing only the images, the bounding boxes in the respective 
# images are taken as source and the image around the bounding boxes is 
# constructed taking the target image size and bounding box dimensions into 
# consideration.
# 
# CURRENTLY NOT IMPLEMENTED:
# This script can also perform data augmentation to increase the overall 
# amount of images. This will be done by randomly mirroring the source image 
# or by adding noise to the source image. Also adjusting contrast, 
# saturation, and brightness randomly over the whole image dataset may 
# improve the model training.



class BoundingBoxAnnotation:
    def __init__(self, xmlObject = None, name = '', xmin = 0, ymin = 0, xmax = 0, ymax = 0):
        if xmlObject is not None:
            self.name = xmlObject.find('name').text.lower()
            bndbox = xmlObject.find('bndbox')
            self.xmin = float(bndbox.find('xmin').text)
            self.ymin = float(bndbox.find('ymin').text)
            self.xmax = float(bndbox.find('xmax').text)
            self.ymax = float(bndbox.find('ymax').text)
        else:
            self.name = name
            self.xmin = xmin
            self.ymin = ymin
            self.xmax = xmax
            self.ymax = ymax

    def width(self):
        return self.xmax - self.xmin

    def height(self):
        return self.ymax - self.ymin

    def scale(self, scaleX, scaleY):
        self.xmin = self.xmin * scaleX
        self.ymin = self.ymin * scaleY
        self.xmax = self.xmax * scaleX
        self.ymax = self.ymax * scaleY

    def scaleToCenter(self, scaleX, scaleY, centerX, centerY):
        self.xmin = centerX + (self.xmin - centerX) * scaleX
        self.ymin = centerY + (self.ymin - centerY) * scaleY
        self.xmax = centerX + (self.xmax - centerX) * scaleX
        self.ymax = centerY + (self.ymax - centerY) * scaleY

    def crop(self, cropX, cropY, cropW, cropH):
        # self.xmin = clamp(self.xmin - cropX, 0.0, cropW)
        # self.ymin = clamp(self.ymin - cropY, 0.0, cropH)
        # self.xmax = clamp(self.xmax - cropX, 0.0, cropW)
        # self.ymax = clamp(self.ymax - cropY, 0.0, cropH)
        self.xmin = self.xmin - cropX
        self.ymin = self.ymin - cropY
        self.xmax = self.xmax - cropX
        self.ymax = self.ymax - cropY

    def clamp(self, imgW, imgH):
        self.xmin = clamp(self.xmin, 0.0, imgW)
        self.ymin = clamp(self.ymin, 0.0, imgH)
        self.xmax = clamp(self.xmax, 0.0, imgW)
        self.ymax = clamp(self.ymax, 0.0, imgH)

    def isEmpty(self, minSize = 10.0):
        return self.width() < minSize or self.height() < minSize

    def percentW(self, imgW, padding = 0.0):
        factor = (0.0 if self.isTouchingLeftBorder() else 1.0) + (0.0 if self.isTouchingRightBorder(imgW) else 1.0)
        return (self.width() + factor * padding) / imgW

    def percentH(self, imgH, padding = 0.0):
        factor = (0.0 if self.isTouchingTopBorder() else 1.0) + (0.0 if self.isTouchingBottomBorder(imgH) else 1.0)
        return (self.height() + factor * padding) / imgH

    def percentAvg(self, imgW, imgH, padding = 0.0):
        return (self.percentW(imgW, padding) + self.percentH(imgH, padding)) / 2.0

    def centerX(self):
        return (self.xmin + self.xmax) / 2.0

    def centerY(self):
        return (self.ymin + self.ymax) / 2.0

    def isTouchingBorder(self, imgW, imgH):
        return self.xmin <= 3.5 or self.ymin <= 3.5 or self.xmax >= imgW - 3.5 or self.ymax >= imgH - 3.5

    def isTouchingLeftBorder(self):
        return self.xmin <= 3.5

    def isTouchingTopBorder(self):
        return self.ymin <= 3.5

    def isTouchingRightBorder(self, imgW):
        return self.xmax >= imgW - 3.5

    def isTouchingBottomBorder(self, imgH):
        return self.ymax >= imgH - 3.5

    def replaceExistingXmlContent(self, xmlObject):
        if self.isEmpty():
            return False
        xmlObject.find('name').text = self.name
        bndbox = xmlObject.find('bndbox')
        bndbox.find('xmin').text = str(int(round(self.xmin)))
        bndbox.find('ymin').text = str(int(round(self.ymin)))
        bndbox.find('xmax').text = str(int(round(self.xmax)))
        bndbox.find('ymax').text = str(int(round(self.ymax)))
        return True

    def toXml(self, xmlRoot):
        if self.isEmpty():
            return False
        xmlObject = ET.Element('object')
        xmlObject.append(new_et_element('name', self.name))
        xmlObject.append(new_et_element('pose', 'Unspecified'))
        xmlObject.append(new_et_element('truncated', '0'))
        xmlObject.append(new_et_element('difficult', '0'))
        bndbox = ET.Element('bndbox')
        bndbox.append(new_et_element('xmin', str(int(round(self.xmin)))))
        bndbox.append(new_et_element('ymin', str(int(round(self.ymin)))))
        bndbox.append(new_et_element('xmax', str(int(round(self.xmax)))))
        bndbox.append(new_et_element('ymax', str(int(round(self.ymax)))))
        xmlObject.append(bndbox)
        xmlRoot.append(xmlObject)
        return True




def new_et_element(tag, text):
    obj = ET.Element(tag)
    obj.text = text
    return obj


def create_path(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def clamp(number, _min, _max):
    return max(_min, min(_max, number))


def get_file_name(path):
    base_dir = os.path.dirname(path)
    file_name, ext = os.path.splitext(os.path.basename(path))
    ext = ext.replace(".", "")
    return (base_dir, file_name, ext)


def process_image(imageFile, outputPath, x, y):
    (base_dir, file_name, ext) = get_file_name(imageFile)
    xml = os.path.join(base_dir, file_name + '.xml')
    try:
        smart_resize(imageFile, xml, (x, y), outputPath)
    except Exception as e:
        print('[ERROR] error with {}\n file: {}'.format(imageFile, e))
        print('--------------------------------------------------')


def smart_resize(imageFile, xmlFile, targetSize, outputPath):
    (base_dir, file_name, image_file_ext) = get_file_name(imageFile)

    # Prepare the image data
    image = cv2.imread(imageFile)

    imgW = float(image.shape[1])
    imgH = float(image.shape[0])
    targetW = float(targetSize[0])
    targetH = float(targetSize[1])
    scaleX = targetW / imgW
    scaleY = targetH / imgH

    if (not Path(xmlFile).exists):
        # Don't resize the image file, if no XML annotation data was found
        print(f"No XML file was found for {file_name}.{image_file_ext} in {base_dir}. Image won\'t be resized!")
    else:
        fileCounter = 0

        # Prepare the XML data
        bboxAnnotations = []
        xmlRoot = ET.parse(xmlFile).getroot()
        xmlObjects = xmlRoot.findall('object')
        for xmlObject in xmlObjects:
            bboxAnnotations.append(BoundingBoxAnnotation(xmlObject))

        numObjects = len(bboxAnnotations)
        if (numObjects == 0):
            # Don't resize the image file, if no bounding boxes were found in the XML annotation file
            print(f"No bounding boxes were found in {file_name}.xml in {base_dir}. Image won\'t be resized!")
        
        elif (numObjects == 1):
            if scaleY > scaleX:
                # Source image's width is larger than target width
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleY, scaleY, bboxAnnotationsCopy)
                if (bboxAnnotationsCopy[0].width() > targetW):
                    fileCounter = saveCroppedLeftTopAndRightBottomImageParts(imageCopy, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotationsCopy, fileCounter, 0.25)
                    fileCounter = saveBoundingBox(image, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotations, fileCounter)
                else:
                    imageCopy = cropImageToCenter(imageCopy, bboxAnnotationsCopy[0].centerX(), bboxAnnotationsCopy[0].centerY(), int(targetW), int(targetH), bboxAnnotationsCopy)
                    fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)
            elif scaleX > scaleY:
                # Source image's height is larger than target height
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleX, scaleX, bboxAnnotationsCopy)
                if (bboxAnnotationsCopy[0].height() > targetH):
                    fileCounter = saveCroppedLeftTopAndRightBottomImageParts(imageCopy, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotationsCopy, fileCounter, 0.25)
                    fileCounter = saveBoundingBox(image, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotations, fileCounter)
                else:
                    imageCopy = cropImageToCenter(imageCopy, bboxAnnotationsCopy[0].centerX(), bboxAnnotationsCopy[0].centerY(), int(targetW), int(targetH), bboxAnnotationsCopy)
                    fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)
            else: # scaleX == scaleY
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleX, scaleY, bboxAnnotationsCopy)
                fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)

        else: # (numObjects > 1):
            if scaleY > scaleX:
                # Source image's width is larger than target width
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleY, scaleY, bboxAnnotationsCopy)
                combined = combineBoundingBoxes(bboxAnnotationsCopy)
                if (combined.width() > targetW):
                    fileCounter = saveCroppedLeftTopAndRightBottomImageParts(imageCopy, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotationsCopy, fileCounter)
                else:
                    imageCopy = cropImageToCenter(imageCopy, combined.centerX(), combined.centerY(), int(targetW), int(targetH), bboxAnnotationsCopy)
                    fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)

                fileCounter = saveZoomedBoundingBoxes(image, scaleY, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotations, fileCounter)
            elif scaleX > scaleY:
                # Source image's height is larger than target height
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleX, scaleX, bboxAnnotationsCopy)
                combined = combineBoundingBoxes(bboxAnnotationsCopy)
                if (combined.height() > targetH):
                    fileCounter = saveCroppedLeftTopAndRightBottomImageParts(imageCopy, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotationsCopy, fileCounter)
                else:
                    imageCopy = cropImageToCenter(imageCopy, combined.centerX(), combined.centerY(), int(targetW), int(targetH), bboxAnnotationsCopy)
                    fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)

                fileCounter = saveZoomedBoundingBoxes(image, scaleX, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotations, fileCounter)
            else: # scaleX == scaleY
                bboxAnnotationsCopy = deepcopy(bboxAnnotations)
                imageCopy = scaleImage(image, scaleX, scaleY, bboxAnnotationsCopy)
                fileCounter = saveAsCopy(imageCopy, xmlRoot, file_name, image_file_ext, outputPath, bboxAnnotationsCopy, fileCounter)

                fileCounter = saveZoomedBoundingBoxes(image, scaleX, xmlRoot, file_name, image_file_ext, targetW, targetH, outputPath, bboxAnnotations, fileCounter)


def deepcopy(arr):
    return [copy.deepcopy(x) for x in arr]

def combineBoundingBoxes(bboxAnnotations):
    xMin = min([bbox.xmin for bbox in bboxAnnotations])
    yMin = min([bbox.ymin for bbox in bboxAnnotations])
    xMax = max([bbox.xmax for bbox in bboxAnnotations])
    yMax = max([bbox.ymax for bbox in bboxAnnotations])
    return BoundingBoxAnnotation(None, '', xMin, yMin, xMax, yMax)

def scaleImage(image, scaleX, scaleY, bboxAnnotations):
    for bbox in bboxAnnotations:
        bbox.scale(scaleX, scaleY)
    interp = cv2.INTER_LINEAR if (scaleX * scaleY > 1.0) else cv2.INTER_AREA
    return cv2.resize(image, None, fx=scaleX, fy=scaleY, interpolation=interp)

def scaleImageToCenter(image, scaleX, scaleY, centerX, centerY, bboxAnnotations):
    imgH, imgW = image.shape[:2]
    for bbox in bboxAnnotations:
        bbox.scaleToCenter(scaleX, scaleY, centerX, centerY)
    interp = cv2.INTER_LINEAR if (scaleX * scaleY > 1.0) else cv2.INTER_AREA
    M = np.float32([
        [scaleX, 0, centerX * (1 - scaleX)],
        [0, scaleY, centerY * (1 - scaleY)]
    ])
    temp = cv2.warpAffine(image, M, (imgW, imgH), flags=interp)

    # rect = BoundingBoxAnnotation(None, '', 0, 0, imgW, imgH)
    # rect.scaleToCenter(scaleX, scaleY, centerX, centerY)
    # (x, y, w, h) = (int(round(rect.xmin)), int(round(rect.ymin)), int(round(rect.width())), int(round(rect.height())))
    # for bbox in bboxAnnotations:
    #     bbox.crop(x, y, w, h)
    # temp = cropImage(temp, x, y, w, h, bboxAnnotations)

    return temp

def resizeImage(image, newSizeX, newSizeY, bboxAnnotations):
    return scaleImage(image, newSizeX / image.shape[1], newSizeY / image.shape[0], bboxAnnotations)

def resizeImageToCenter(image, newSizeX, newSizeY, centerX, centerY, bboxAnnotations):
    return scaleImageToCenter(image, newSizeX / image.shape[1], newSizeY / image.shape[0], centerX, centerY, bboxAnnotations)

def enlargeImage(image, x, y, w, h):
    top = -y if y < 0 else 0
    bottom = (y + h) - image.shape[0] if (y + h) > image.shape[0] else 0
    left = -x if x < 0 else 0
    right = (x + w) - image.shape[1] if (x + w) > image.shape[1] else 0
    color = [0, 0, 0]
    return cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

def cropImage(image, x, y, w, h, bboxAnnotations):
    if (x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]):
        image = enlargeImage(image, x, y, w, h)
        for bbox in bboxAnnotations:
            bbox.crop(min(x, 0), min(y, 0), image.shape[1], image.shape[0])

    if (x < 0):
        # w += x
        x = 0
    if (y < 0):
        # h += y
        y = 0
    # if (x + w > image.shape[1]):
    #     w = image.shape[1] - x
    # if (y + h > image.shape[0]):
    #     h = image.shape[0] - y

    for bbox in bboxAnnotations:
        bbox.crop(x, y, w, h)
    return image[y:y+h, x:x+w]

def cropImageToCenter(image, centerX, centerY, w, h, bboxAnnotations, clampValues = True):
    x = int(centerX - w / 2)
    y = int(centerY - h / 2)
    if (clampValues):
        x = clamp(x, 0, image.shape[1] - w)
        y = clamp(y, 0, image.shape[0] - h)
        w = clamp(w, 0, image.shape[1] - x)
        h = clamp(h, 0, image.shape[0] - y)
    return cropImage(image, x, y, w, h, bboxAnnotations)

def saveCroppedLeftTopAndRightBottomImageParts(image, origXmlRoot, imageFileName, imageFileExt, targetW, targetH, outputPath, bboxAnnotations, fileCounter, minSizePercent = 0.05):
    minSize = max(min(targetW * minSizePercent, targetH * minSizePercent), 10.0)

    bboxAnnotations_left_top_part = deepcopy(bboxAnnotations)
    img_left_top_part = cropImage(image, 0, 0, int(targetW), int(targetH), bboxAnnotations_left_top_part)
    fileCounter = saveAsCopy(img_left_top_part, origXmlRoot, imageFileName, imageFileExt, outputPath, bboxAnnotations_left_top_part, fileCounter, minSize)

    imgW = float(image.shape[1])
    tX = int(imgW - targetW)
    imgH = float(image.shape[0])
    tY = int(imgH - targetH)
    img_right_bottom_part = cropImage(image, tX, tY, int(targetW), int(targetH), bboxAnnotations)
    fileCounter = saveAsCopy(img_right_bottom_part, origXmlRoot, imageFileName, imageFileExt, outputPath, bboxAnnotations, fileCounter, minSize)
    return fileCounter

def saveZoomedBoundingBoxes(image, scale, origXmlRoot, imageFileName, imageFileExt, targetW, targetH, outputPath, bboxAnnotations, fileCounter):
    for index, bbox in enumerate(bboxAnnotations):
        bboxAnnotationsCopy = deepcopy(bboxAnnotations)
        bboxCopy = bboxAnnotationsCopy[index]
        percentMin = max(bboxCopy.percentW(targetW), bboxCopy.percentH(targetH))
        if (percentMin < 0.5 and not bboxCopy.isTouchingBorder(image.shape[1], image.shape[0])):
            imageCopy = cropImageToCenter(image, bboxCopy.centerX(), bboxCopy.centerY(), int(targetW), int(targetH), bboxAnnotationsCopy, False)
            percentMin = max(bboxCopy.percentW(targetW, 20.0), bboxCopy.percentH(targetH, 20.0))
            rescale = min(1.0 / percentMin, 4.0 * scale)
            imageCopy = scaleImageToCenter(imageCopy, rescale, rescale, bboxCopy.centerX(), bboxCopy.centerY(), bboxAnnotationsCopy)
            fileCounter = saveAsCopy(imageCopy, origXmlRoot, imageFileName, imageFileExt, outputPath, bboxAnnotationsCopy, fileCounter)
    return fileCounter

def saveBoundingBox(image, origXmlRoot, imageFileName, imageFileExt, targetW, targetH, outputPath, bboxAnnotations, fileCounter):
        bboxAnnotationsCopy = deepcopy(bboxAnnotations)
        bbox = bboxAnnotationsCopy[0]
        scaleX = targetW / bbox.width()
        scaleY = targetH / bbox.height()
        newscale = min(scaleX, scaleY)
        imageCopy = scaleImageToCenter(image, newscale, newscale, bbox.centerX(), bbox.centerY(), bboxAnnotationsCopy)
        imageCopy = cropImageToCenter(imageCopy, bbox.centerX(), bbox.centerY(), int(targetW), int(targetH), bboxAnnotationsCopy, True)
        fileCounter = saveAsCopy(imageCopy, origXmlRoot, imageFileName, imageFileExt, outputPath, bboxAnnotationsCopy, fileCounter)
        return fileCounter

def saveAsCopy(image, origXmlRoot, imageFileName, imageFileExt, outputPath, bboxAnnotations, fileCounter, minSize = 10.0):
    for bbox in bboxAnnotations:
        bbox.clamp(image.shape[1], image.shape[0])

    bboxAnnotations = [bbox for bbox in bboxAnnotations if not bbox.isEmpty(minSize)]

    if bboxAnnotations is None or len(bboxAnnotations) == 0:
        return fileCounter

    # FOR TESTING:
    # imageFileName = str(imageFileName + '_COPY') # FOR TESTING ONLY

    if (fileCounter > 0):
        imageFileName = str(imageFileName + '_' + str(fileCounter))
    imageFileNameWithExt = str(imageFileName + '.' + imageFileExt)
    newImageFile = os.path.join(outputPath, imageFileNameWithExt)
    cv2.imwrite(newImageFile, image)

    if (origXmlRoot is not None):
        xmlRoot = copy.deepcopy(origXmlRoot)
        xmlRoot.find('filename').text = imageFileNameWithExt
        xmlRoot.find('path').text = str(newImageFile)

        size_node = xmlRoot.find('size')
        imgW = image.shape[1]
        imgH = image.shape[0]
        size_node.find('width').text = str(imgW)
        size_node.find('height').text = str(imgH)
        
        xmlObjects = xmlRoot.findall('object')
        for xmlObject in xmlObjects:
            xmlRoot.remove(xmlObject)

        for bbox in bboxAnnotations:
            bbox.toXml(xmlRoot)

        tree = ET.ElementTree(xmlRoot)
        tree.write(os.path.join(outputPath, imageFileName + '.xml'))

    return fileCounter + 1




IMAGE_FORMATS = ('.jpeg', '.JPEG', '.png', '.PNG', '.jpg', '.JPG')

def smart_resize_all(inPath, outPath, x, y):
    create_path(outPath)
    for root, _, files in os.walk(inPath):
            out_path = outPath + root[len(inPath):]
            create_path(out_path)

            for file in files:
                if file.endswith(IMAGE_FORMATS):
                    image_file = os.path.join(root, file)
                    process_image(image_file, out_path, x, y)









# Returns the name of the folder from the given path.
def getFolderNameOnly(path):
    return os.path.basename(os.path.normpath(path))


# Checks if any file in the given list is of type XML.
def checkIfAFileIsOfTypeXMLExists(files):
    for file in files:
        if file.endswith('.xml'):
            return True
    return False


# Checks if every directory in the given list is either a hidden or a system directory.
def onlyHiddenOrSystemDirsExist(dirs):
    for dr in dirs:
        if not (dr.startswith('.') or dr.startswith('@')):
            return False
    return True


# Creates a temporary folder structure under the given tempPath.
def createTempFolderStructure(tempPath, trainPath, valPath, testPath):
    try:
        shutil.rmtree(tempPath)
    except:
        abc="" # Do nothing, if temp folder does not exist

    try:
        Path(tempPath).mkdir(parents=True, exist_ok=True)
    except:
        print(f"ERROR: Could not create temporary folder {tempPath}")
        quit()

    trainPath = os.path.join(tempPath, trainPath)
    valPath = os.path.join(tempPath, valPath)
    testPath = os.path.join(tempPath, testPath)
    Path(trainPath).mkdir(parents=True, exist_ok=True)
    Path(valPath).mkdir(parents=True, exist_ok=True)
    Path(testPath).mkdir(parents=True, exist_ok=True)
    return (trainPath, valPath, testPath)


# Returns a list of available classes in the given directory.
def getAvailableClassesInDirectory(imageDatasetsPath):
    dirsList = []
    for root, dirs, files in os.walk(imageDatasetsPath):
        if len(files) > 0 and checkIfAFileIsOfTypeXMLExists(files) and (len(dirs) == 0 or onlyHiddenOrSystemDirsExist(dirs)):
            dirsList.append((getFolderNameOnly(root).lower(), root))
    return dirsList


# Copy the given image to the given path.
def copyFile(copy_me, new_path):
    try:
        fn = copy_me.name
        base_fn = copy_me.stem
        parent_path = copy_me.parent
        parent_dir_suffix = os.path.basename(parent_path) + '_'
        new_image_file_name = os.path.join(new_path, parent_dir_suffix + fn)
        shutil.copy(copy_me, new_image_file_name)
        xml_fn = base_fn + '.xml'
        xml_me = os.path.join(parent_path, xml_fn)
        new_xml_file_name = os.path.join(new_path, parent_dir_suffix + xml_fn)
        if (os.path.isfile(xml_me)):
            with open(xml_me, 'r') as fxml:
                xml_content = fxml.read()
            xml_content = xml_content.replace('<filename>' + fn + '</filename>', '<filename>' + parent_dir_suffix + fn + '</filename>')
            with open(new_xml_file_name, 'w') as fxml_new:
                fxml_new.write(xml_content)
            # shutil.copy(xml_me, os.path.join(new_path, parent_dir_suffix + xml_fn))
        return new_image_file_name
    except Exception as e:
        print(f"ERROR: Could not copy file {copy_me} to {new_path}. {e}")
        return None


# Copy a random image to the given path and remove it from the input data.
def copyRandomFile(new_path, inputData):
    copy_me = random.choice(inputData)
    copyFile(copy_me, new_path)
    inputData.remove(copy_me)
    return inputData


# Move a random image to the given path and remove it from the input data.
def moveFile(move_me, new_path):
    try:
        fn = move_me.name
        base_fn = move_me.stem
        parent_path = move_me.parent
        parent_dir_suffix = os.path.basename(parent_path) + '_'
        new_image_file_name = os.path.join(new_path, parent_dir_suffix + fn)
        shutil.move(move_me, new_image_file_name)
        xml_fn = base_fn + '.xml'
        xml_me = os.path.join(parent_path, xml_fn)
        new_xml_file_name = os.path.join(new_path, parent_dir_suffix + xml_fn)
        if (os.path.isfile(xml_me)):
            with open(xml_me, 'r') as fxml:
                xml_content = fxml.read()
            xml_content = xml_content.replace('<filename>' + fn + '</filename>', '<filename>' + parent_dir_suffix + fn + '</filename>')
            with open(xml_me, 'w') as fxml:
                fxml.write(xml_content)
            shutil.move(xml_me, new_xml_file_name)
        return new_image_file_name
    except Exception as e:
        print(f"ERROR: Could not move file {move_me} to {new_path}. {e}")
        return None


# Move a random image to the given path and remove it from the input data.
def moveRandomFile(new_path, inputData):
    move_me = random.choice(inputData)
    moveFile(move_me, new_path)
    inputData.remove(move_me)
    return inputData


# Checks if an XML file exists for the given image.
def xmlFileExistsForImage(imagePath):
    xmlPath = imagePath.with_suffix('.xml')
    return xmlPath.exists()


# Collects labeled images for user defined labels from the given path.
def collectImages(labels, imageDatasetsPath, limitPerLabel):
    availableClasses = getAvailableClassesInDirectory(imageDatasetsPath)
    inputData = []
    for label in labels:
        foundImages = 0
        for cls in availableClasses:
            if label == cls[0] and foundImages < limitPerLabel:
                srcPath = cls[1]
                jpgFilesList = [path for path in Path(srcPath).rglob('*.jpg')]
                for jpg in jpgFilesList: # FIXME: Improve this function to take a random set of images from the jpgFilesList if limitPerLabel is smaller than the len(jpgFilesList)
                    if xmlFileExistsForImage(jpg):
                        inputData.append(jpg)
                        foundImages += 1
                        if foundImages >= limitPerLabel:
                            break
    return inputData


# Copies all given labeled images to the given path.
def copyImages(inputData, outputPath):
    outputData = []
    for img in inputData:
        result = copyFile(img, outputPath)
        if result is not None:
            outputData.append(result)
    return outputData


# Resizes the given images to the given size.
def smartResizeImages(inputPath, x, y):
    smart_resize_all(inputPath, inputPath, x, y)
    outputData = [path for path in Path(inputPath).rglob('*.jpg')]
    return outputData


# Copies the given images to the given train, val and test directories.
def copyAndDistributeImages(inputData, trainTempPath, trainPercent, valTempPath, valPercent, testTempPath):
    numFiles = len(inputData)
    numTrain = int(numFiles * trainPercent)
    numVal = int(numFiles * valPercent)
    numTest = numFiles - numTrain - numVal
    print(f"Found a total of {numFiles} images. ({numTrain} training, {numVal} validation, {numTest} test)")

    # Copy numTrain random files to train folder
    print(f"Copying {numTrain} images with annotation data to '{trainTempPath}' ......")
    for i in range(numTrain):
        inputData = copyRandomFile(trainTempPath, inputData)

    # Copy numVal random files to validation folder
    print(f"Copying {numVal} images with annotation data to '{valTempPath}' ......")
    for i in range(numVal):
        inputData = copyRandomFile(valTempPath, inputData)

    # Copy remaining files to test folder
    print(f"Copying {numTest} images with annotation data to '{testTempPath}' ......")
    for i in range(numTest):
        inputData = copyRandomFile(testTempPath, inputData)


# Moves the given images to the given train, val and test directories.
def distributeImages(inputData, trainTempPath, trainPercent, valTempPath, valPercent, testTempPath):
    numFiles = len(inputData)
    numTrain = int(numFiles * trainPercent)
    numVal = int(numFiles * valPercent)
    numTest = numFiles - numTrain - numVal
    print(f"Found a total of {numFiles} images.") # Distribution will be: {numTrain} -> training, {numVal} -> validation, {numTest} -> test.")

    # Copy numTrain random files to train folder
    print(f"Moving {numTrain} images with annotation data to '{trainTempPath}' ......")
    for i in range(numTrain):
        inputData = moveRandomFile(trainTempPath, inputData)

    # Copy numVal random files to validation folder
    print(f"Moving {numVal} images with annotation data to '{valTempPath}' ......")
    for i in range(numVal):
        inputData = moveRandomFile(valTempPath, inputData)

    # Copy remaining files to test folder
    print(f"Moving {numTest} images with annotation data to '{testTempPath}' ......")
    for i in range(numTest):
        inputData = moveRandomFile(testTempPath, inputData)
