<b>Object Detection Utils</b>

<p>This repository contains scripts to help you with the image preparation and machine learning model training for object detection tasks.</p>

<p>For the model training, we need a Python 3.9 virtual environment.<br>
Use the following commands to install python 3.9 and the virtual environment in a Linux environment.</p>

<code>$ sudo apt install python3.9</code><br>
<code>$ sudo apt install python3.9-venv</code><br>

<p>If python3.9 cannot be found in the available packages, add the repository ppa:deadsnakes/ppa by using the following commands:</p>

<code>$ sudo apt update</code><br>
<code>$ sudo apt install software-properties-common</code><br>
<code>$ sudo add-apt-repository ppa:deadsnakes/ppa</code><br>
<code>$ sudo apt update</code><br>
<code>$ sudo apt install python3.9</code><br>
<code>$ sudo apt install python3.9-venv</code><br>

<p>Next we are going to activate the virtual environment and install all necessary dependencies.</p>

<code>$ python3.9 -m venv .py39</code><br>
<code>$ source .py39/bin/activate</code><br>
<code>(py39) $ pip install -r requirements.txt</code><br>
