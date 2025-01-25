sudo apt install libsm6 libxext6 libgl1


#!/bin/bash
source .py39/bin/activate

pip install --upgrade pip

cd "/run/user/$UID/gvfs/smb-share:server=ds218.local,share=documents/Machine Learning/scripts"
pip install -r requirements.txt


pip install tflite-model-maker
pip install tflite-support
# os.system("pip install datasets==2.15")
# os.system("pip install ipykernel")
# os.system("pip uninstall numpy")
# os.system("pip install --no-dependencies --upgrade numpy==1.23.4")
# os.system("pip install pycocotools")

# os.system("pip install --ignore-installed --upgrade tensorflow-2.5.3-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.6.3-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.7.1-cp39-cp39-linux_x86_64.whl") // NOT WORKING
# os.system("pip install --ignore-installed --upgrade tensorflow-2.8.0-cp39-cp39-linux_x86_64.whl")
# os.system("pip install --ignore-installed --upgrade tensorflow-2.18.0-cp310-cp310-linux_x86_64.whl") // NOT WORKING as built for Python 3.10
# os.system("pip install tensorflow-recommenders==0.6.0")
# os.system("pip install protobuf==3.20.*")
# os.system("pip uninstall numpy")
# os.system("pip install --no-dependencies --upgrade numpy==1.23.4")

pip install ai-edge-litert
pip install mediapipe-model-maker
