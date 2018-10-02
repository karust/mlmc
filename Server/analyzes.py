import urllib.request
import json
from Static import static
import os
import time
import asyncio

cwd = os.getcwd()


class File(object):
    def __init__(self, filename, totalChunks):
        self.filename = filename
        self.processedChunks = 0
        self.totalChunks = totalChunks
        self.lastChunk = 0
        self.chunks = {}


class Analyzes(object):
    def __init__(self, file):
        self.file = file
        self.res = None
        self.time = 0

    def start_analysis(self):
        start = time.time()

        pe = static.PortableExecutable(cwd + '/Server/uploaded/' + self.file.filename)
        res = pe.run()

        end = time.time()
        self.time = end - start

        if res == None:
            self.res = "NotPE"
            return

        myurl = 'http://127.0.0.1:4546/analyze'
        req = urllib.request.Request(myurl)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(res)
        jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
        req.add_header('Content-Length', len(jsondataasbytes))

        response = urllib.request.urlopen(req, jsondataasbytes)

        res['prediction'] = eval(response.read())['prediction']
        self.res = res


if __name__ == "__main__":
    pass