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

## Launching
Project consists of 3 parts:
* Server - Web server for classification of PE files.
* Static - Code for classifying PE files by their static features. 
    1) collect_data.py - collect static features of PE files;
    2) training.py - train neural network on collected data;
    3) analyzer.py - server with the trained neural network on board.
* Auxillary - Helper modules. Currently there is a script which helps to collect data in one place to further analysis.

### Launching app (locally)
```
python3 main.py
```

## Using app
1. Head on to http://127.0.0.1:8888/ in your favorite browser and see menu where you can select one file to analyze or even folder:
(image)

2. If there is no error, after some time file should be uploaded:
(image)

3. Then you can navigate to analysis menu where you can see the results and play with sorting of files:
(image)

4. If you interested in more detailed information you can click by the file and see its features:
(image)
