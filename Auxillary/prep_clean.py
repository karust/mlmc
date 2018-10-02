from os.path import join, basename, getsize, isdir, isfile
from os import remove, chmod
import os
from shutil import rmtree, copyfile, move
import glob
import json
import sys
import ctypes

def run_as_admin(argv=None, debug=False):
    shell32 = ctypes.windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True

    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments =argv[1:]
    else:
        arguments = argv
    argument_line = u' '.join(arguments)
    executable = sys.executable
    ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    if int(ret) <= 32:
        return False
    return None


def label_VS(files_path, labels_path, destination_path = None, move_files = False):
    file = open(labels_path, 'r')
    labels = json.load(file)

    total_pe = 0
    exe_files = []
    for label in labels:
        if(label['sig'].__contains__('PE32')):
            exe_files.append(label['f'])
            total_pe+=1
    print("Total PE files in Archive: ", total_pe)

    labeled = 0
    print("Collecting files in directory (May take some time)")
    if destination_path:
        for filename in os.listdir(files_path):
            if filename in exe_files:
                if move_files:
                    move(files_path+filename, destination_path+filename+'.exe')
                else:
                    copyfile(files_path+filename, destination_path+filename+'.exe')

                exe_files.remove(filename)
                labeled += 1
                print("{0}/{1}".format(labeled, total_pe))
    else:
        for filename in os.listdir(files_path):
            if filename in exe_files:
                os.rename(files_path+filename, files_path+filename+'.exe')
                exe_files.remove(filename)
                labeled += 1
                print("{0}/{1}".format(labeled, total_pe))
    print("Processed %s files" % labeled)


def clean_fodler(folder):
    """Delete files if not .dll .exe .sys"""

    run_as_admin()
    my_folder = folder

    print("Collecting folder data...")
    pe_files = []
    for ext in ('*.dll', '*.exe', '*.sys'):
        print("Collecting '" + ext + "' files")
        pe_files.extend(glob.iglob(my_folder + '**/' + ext, recursive=True))

    all_files = []
    all_files.extend(glob.iglob(join(my_folder + '**/', '*'), recursive=True))

    print("Removing files...")
    len_files = len(all_files)
    for i, file in enumerate(all_files):
        print('{0:.2f}%'.format((i+1) / len_files * 100))
        if file not in pe_files and isfile(file):
            try:
                remove(file)
            except PermissionError:
                try:
                    chmod(file, 0o777)
                    remove(file)
                except FileNotFoundError:
                    pass
            except FileNotFoundError:
                pass

    print("Removing empty folders...")
    folders = []
    folders.extend(glob.iglob(join(my_folder + '\\**', '*'), recursive=True))
    folders = [f for f in folders if isdir(f)]

    len_folders = len(folders)
    for i, folder in enumerate(folders):
        print('{0:.2f}%'.format((i+1) / len_folders * 100))
        if sum(getsize(x) for x in glob.iglob(folder + '\\**')) == 0 and isdir(folder):
            try:
                chmod(folder, 0o777)
                rmtree(folder)
            except PermissionError:
                pass
            except FileNotFoundError:
                pass

if __name__ == "__main__":
    clean_fodler("F:\\Ungrd-Research\\PE\\Legal_PE\\WinXP\\")

    """label_VS(files_path='F:/Ungrd-Research/Malwares/VirusShare_x86-64_WinEXE/',
                labels_path='F:/Ungrd-Research/Malwares/archives/VirusShare_x86-64_WinEXE_20130711.zip.file.json',
                destination_path='F:/Ungrd-Research/Malwares/Binaries/',
                move_files = True
                )"""