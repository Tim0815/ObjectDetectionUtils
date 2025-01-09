This repository contains scripts to help you with the image preparation and machine learning model training for object detection tasks.


For the model training, we need a Python 3.9 virtual environment.
Use the following commands to install python 3.9 and the virtual environment in a Linux environment.

$ sudo apt install python3.9

(If python3.9 cannot be found in the available packages, add the repository ppa:deadsnakes/ppa by using the following commands:
$ sudo apt update
$ sudo apt install software-properties-common
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.9)

$ sudo apt install python3.9-venv


Next we are going to activate the virtual environment and install all necessary dependencies.

$ python3.9 -m venv .py39
$ source .py39/bin/activate
(py39) $ pip install -r requirements.txt
