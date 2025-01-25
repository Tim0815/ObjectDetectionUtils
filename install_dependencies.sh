sudo apt install libsm6 libxext6 libgl1


#!/bin/bash
source .py39/bin/activate

pip install --upgrade pip

cd "/run/user/$UID/gvfs/smb-share:server=ds218.local,share=documents/Machine Learning/scripts"
pip install -r requirements.txt


pip install tensorflow==2.8.4
pip install tflite-model-maker
pip install tflite-support
pip install datasets==2.15
pip install ipykernel

# os.system("pip install --ignore-installed --upgrade tensorflow-2.5.3-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.6.3-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.7.1-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.8.0-cp39-cp39-linux_x86_64.whl") // seems to work

pip install --no-dependencies numpy==1.23.4
pip install pycocotools
pip install tensorflow-recommenders==0.6.0
pip install protobuf==3.20.*
pip install ai-edge-litert
pip install mediapipe-model-maker
