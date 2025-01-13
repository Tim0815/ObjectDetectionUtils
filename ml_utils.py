import sys, platform, os, subprocess, time, random, shutil, cv2
from pathlib import Path
import xml.etree.ElementTree as ET
from math import floor
from smart_resize_images import resize_all


# Returns the name of the folder from the given path.
def getFolderNameOnly(path):
    return os.path.basename(os.path.normpath(path))


# Checks if any file in the given list is of type XML.
def checkIfAFileIsOfTypeXMLExists(files):
    for file in files:
        if file.endswith('.xml'):
            return True
    return False


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
        if len(files) > 0 and checkIfAFileIsOfTypeXMLExists(files):
            if not any(os.scandir(os.path.join(root, dir))):
                dirsList.append((getFolderNameOnly(root), root))
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
def collectImages(labels, imageDatasetsPath):
    availableClasses = getAvailableClassesInDirectory(imageDatasetsPath)
    inputData = []
    for label in labels:
        for cls in availableClasses:
            if label == cls[0]:
                srcPath = cls[1]
                jpgFilesList = [path for path in Path(srcPath).rglob('*.jpg')]
                for jpg in jpgFilesList:
                    if xmlFileExistsForImage(jpg):
                        inputData.append(jpg)
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
    resize_all(inputPath, inputPath, x, y)
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
    print(f"Found a total of {numFiles} images. ({numTrain} training, {numVal} validation, {numTest} test)")

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
