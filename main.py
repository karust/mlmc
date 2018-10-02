from Server.server import Server

import subprocess
import sys
import threading
import ctypes
import os

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

def runAnalyzer():
    proc = subprocess.Popen([sys.executable, "Static/analyzer.py"], shell=False)
    proc.communicate()
    #shell32 = ctypes.windll.shell32
    #ret = shell32.ShellExecuteW(None, u"runas", sys.executable, "Static/analyzer.py", None, 1)


if __name__ == "__main__":
    run_as_admin()


    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    
    threading.Thread(target=runAnalyzer).start()

    server = Server(ip='192.168.0.101', port=80)
    server.run()
