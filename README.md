# Machine Learning Malware Classifyer Backend (MLMCB)

## What is this?
This is backend for machine learning classifier of malwares. It can classify given PE file as malicious or legitimate with a probability (from 0.0 to 1.0). 

Currently MLMCB implements approach of static analysis of files - it collects some static parameters of file, that are then fed into neural network, which was previously trained on a tousands of malicious and legitimate samples. 


*Note: code not fully ported to Linux.*  
*Note: Server now only tested on Ubuntu-18.*
## Installation
* Clone repository:
```
git clone https://github.com/karust/av_back.git

cd av_back
```

* Create Python virtual enviournment and activate it:
```
virtualenv mlmcb

source ./mlmcb/bin/activate
```

* Install required libraries:
```
pip3 install -r requirements.txt
```

## Description 
Project consists of 3 parts:
* Server - Web server for classification of PE files.
* Static - Code for classifying PE files by their static features. 
    1) collect_data.py - collect static features of PE files;
    2) training.py - train neural network on collected data;
    3) analyzer.py - server with the trained neural network on board.
* Auxillary - Helper modules. Currently there is a script which helps to collect data in one place to further analysis.

## Launching (locally)
```
python3 main.py
```

## Using app
1. Head on to http://127.0.0.1:8888/ in your favorite browser and see menu where you can select one file to analyze or even folder:
![image]()
<p align="center">
<img src="https://user-images.githubusercontent.com/43439351/53442563-9bdca480-3a1a-11e9-9f92-28b05f24fff4.png" width="600" height="350"/></p>
    
2. If there is no error, after some time file should be uploaded:
<p align="center">
<img src="https://user-images.githubusercontent.com/43439351/53442830-3341f780-3a1b-11e9-8e45-022d3eccc607.png" width="550" height="250"/></p>

3. Then you can navigate to analysis menu where you can see the results and play with sorting of files:
<p align="center">
<img src="https://user-images.githubusercontent.com/43439351/53442854-48b72180-3a1b-11e9-98b3-310c312c832f.png" width="600" height="320"/></p>

4. If you interested in more detailed information you can click by the file and see its features:
<p align="center">
<img src="https://user-images.githubusercontent.com/43439351/53442936-83b95500-3a1b-11e9-88ea-3a3708d3783a.png" width="570" height="350"/></p>
