import numpy as np
import os

from tflite_model_maker.config import QuantizationConfig
from tflite_model_maker.config import ExportFormat
from tflite_model_maker import model_spec
from tflite_model_maker import object_detector

import tensorflow as tf
assert tf.__version__.startswith('2')
tf.get_logger().setLevel('ERROR')

from pprint import pprint #Pretty printing for output


def trainEfficientDetLite0Model(classes, trainPath, valPath, testPath, modelFileName):
    train_data = object_detector.DataLoader.from_pascal_voc(
        trainPath, #'images/train',
        trainPath,
        classes
    )

    validation_data = object_detector.DataLoader.from_pascal_voc(
        valPath,
        valPath,
        classes
    )

    test_data = object_detector.DataLoader.from_pascal_voc(
        testPath,
        testPath,
        classes
    )

    print("\nUsing an EfficientDet-Lite0 model for training with 320x320 image resolution.")
    spec = object_detector.EfficientDetLite0Spec()

    print("\nTraining starts......")
    model = object_detector.create(train_data=train_data, 
                                model_spec=spec, 
                                validation_data=validation_data, 
                                epochs=50, 
                                batch_size=4, 
                                train_whole_model=True)
    print("\nEvaluating created model")
    print("Evaluation result:") 
    result = model.evaluate(test_data)                             
    pprint(result, width=10)

    LABELS_FILENAME = 'labels.txt'

    print("\nExport model to tflite-format")
    model.export(export_dir='.', tflite_filename=modelFileName, label_filename=LABELS_FILENAME,
                export_format=[ExportFormat.TFLITE, ExportFormat.LABEL])

    print("\n\nEvaluating tflite-model") 
    print("Evaluation result:")             
    result = model.evaluate_tflite(modelFileName, test_data)
    pprint(result, width=10)
    
    return 0
