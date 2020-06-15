import static
import glob
import pandas as pd
import os
import shutil
import time
from multiprocessing import Process, Manager, Lock, Pool
import logging

# create logger with 'spam_application'
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

directories1 = {
        1:['C:/Python34/'],
        0:['C:/Octave/'] 
               }

directories = {
        1:['F:/Ungrd-Research/PE/Malwares/'],  # Malwares 77.184
        0:['F:/Ungrd-Research/PE/Legal_PE/Win10/','F:/Ungrd-Research/PE/Legal_PE/Win7/', 'F:/Ungrd-Research/PE/Legal_PE/WinXP/', ] # Legal 53.572
               }

malware = []
legal = []

files = []
sliced_labeled_files = []

def label(is_malware, ext):
    if is_malware:
        for d in directories[is_malware]:
            for e in ext:
                print("Collecting '" + e + "' files in " + d)
                malware.extend(glob.iglob(d + '**/' + e, recursive=True))
        files.extend(malware)
    else:
        for d in directories[is_malware]:
            for e in ext:
                print("Collecting '" + e + "' files in " + d)
                legal.extend(glob.iglob(d + '**/' + e, recursive=True))
        files.extend(legal)


def mine(files, results):
    for file in files:
        try:
            f = list(file.keys())[0]
            pe = static.PortableExecutable(f)
            res = pe.run()

            res["file"] = f
            res["malware"] = list(file.values())[0]
            results.append(res)

        except Exception as e:
            logger.debug("Exception: {0}, File: {1}".format(e, file))
            continue

def c_data(processes=1):
    all_files = files[:] # For debugging
    files_num = len(all_files)

    def label(file):
        if file in malware:
            return {file:1}
        else:
            return {file:0}
        
    print("\nLabeling files...")
    for s in range(processes):
        print("Labeling for {0} process.".format(s+1))
        if s == processes-1:
            lfiles = all_files[round(files_num/processes)*s:]
        else:
            lfiles = all_files[round(files_num/processes)*s:round(files_num/processes)*(s+1)]
        labeled_files = map(label, lfiles)
        sliced_labeled_files.append(list(labeled_files))

    man = Manager()
    results = man.list()
    
    for proc in range(processes):
        print("Starting {0} process.".format(proc+1))
        Process(target=mine, args=(sliced_labeled_files[proc], results)).start()

    start_time = time.time()
    prev_num = 123
    while True:
        num = len(results)
        if num < files_num:
            if num != prev_num:
                print("{0}/{1}".format(len(results), files_num))
            prev_num = num
            if num % 10000 == 0:
                #fil = glob.iglob('data/*')
                #for f in fil:
                #    os.remove(f)
                data = pd.DataFrame.from_dict(list(results))
                data.to_excel('data/data_{0}.xlsx'.format(num))
            time.sleep(0.02)
            continue
        break
    ex = time.time() - start_time
    print("Execution time {0} seconds for {1} processes".format(ex, processes))
    
    
    data = pd.DataFrame.from_dict(list(results))
    data.to_excel('data/data.xlsx')


if __name__ == "__main__":
    label(1, ['*.dll', '*.exe', '*.sys'])
    label(0, ['*.dll', '*.exe', '*.sys'])

    c_data(processes=4)