from aiohttp import web, ClientSession
import os
import json
import string
import random
from io import BytesIO
import Server.help.multipart as mp
#from multipart import tob
from Static import static
from Server.analyzes import Analyzes, File
import time
import threading

cwd = os.getcwd()

routes = web.RouteTableDef()

upload_path = 'Server/uploaded/'

files = {}
analyzes = {}


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


async def handle_chunks(filename, num, data):
    path = upload_path + filename
    f = files[filename]

    if f.processedChunks == 0:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            print("Permission error: ",filename)
            return False

    if num == f.lastChunk+1:
        with open(path, "ab") as nf:
            nf.write(data.encode("latin-1"))
        f.processedChunks += 1
        f.lastChunk = num
    else:
        f.chunks[num] = data

    for _ in list(f.chunks):
        if f.lastChunk+1 in f.chunks:
            data = f.chunks.pop(f.lastChunk+1)
            with open(path, "ab") as nf:
                nf.write(data.encode("latin-1"))
            f.processedChunks += 1
            f.lastChunk = f.lastChunk+1

    if int(f.totalChunks) == num:
        return f


#CORS Header
@web.middleware
async def header_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:8000'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Server'] = 'None of your business'
    return response


@routes.view("/")
class Main(web.View):
    async def get(self):
        return web.FileResponse(cwd+'/Server/static/index.html')


@routes.view("/completed")
class Completed(web.View):
    async def get(self):
        data = self.request.query
        response = []
        for an in analyzes:
            if analyzes[an].res != "NotPE" and analyzes[an].res:
                f = {'name':analyzes[an].file.filename,
                      'location':'/',
                      "info":'Addition information is not available',
                      "time":analyzes[an].time,
                      "prediction": analyzes[an].res["prediction"]
                        }
                response.append(f)
        return web.Response(text=json.dumps(response), status=200)


@routes.view("/analyzes")
class Analyzing(web.View):
    async def get(self):
        data = self.request.query
        response = {}
        for an in analyzes:
            if analyzes[an].res == None:
                response[analyzes[an].file.filename] = True
            elif analyzes[an].res == "NotPE":
                response[analyzes[an].file.filename] = "NotPE"
            else:
                response[analyzes[an].file.filename] = False

        return web.Response(text=json.dumps(response), status=200)



@routes.view("/results")
class Results(web.View):
    async def get(self):
        try:
            data = self.request.query
            filename = data['filename']


            an = analyzes[filename]
            res = an.res
            return web.Response(text=json.dumps(res), status=200)

        except json.decoder.JSONDecodeError:
            return web.HTTPNoContent()


@routes.view('/upload')
class FileLoad(web.View):
    async def post(self):
        pack = await self.request.content.read()
        s = pack.split(b"\r")[0][2:]
        p = mp.MultipartParser(BytesIO(mp.tob(pack)), s)
        blob = p.parts()

        """
            0  :  chunkNumber
            1  :  chunkSize
            2  :  currentChunkSize
            3  :  totalSize
            4  :  identifier
            5  :  filename
            6  :  relativePath
            7  :  totalChunks
            8  :  file
        """
        curr_chunkNumber = int(blob[0].value)
        totalChunks = blob[7].value
        filename = blob[5].value
        file = blob[8].value

        ret = None
        try:
            if filename not in files:
                f = File(filename, totalChunks)
                files[filename] = f
                ret = await handle_chunks(filename, curr_chunkNumber, file)
            else:
                ret = await handle_chunks(filename, curr_chunkNumber, file)
            if ret == False:
                return web.HTTPExpectationFailed()
            elif ret:
                analyz = Analyzes(ret)
                analyzes[filename] = analyz
                threading.Thread(target=analyz.start_analysis).start()

        except Exception as e:
            print(e)
            return web.HTTPServerError()
        return web.HTTPOk()

    async def options(self):
        return web.Response(text=json.dumps({}), status=200)


class Server(object):
    def __init__(self, ip="127.0.0.1", port=4545):
        self.ip = ip
        self.port = port
        self.app = web.Application(middlewares=[header_middleware])
        self.app.add_routes([web.static('/static/', cwd+'/Server/static/', follow_symlinks=True)])
        self.app.add_routes(routes)

    def run(self):
        print("--- Web server is running ---")
        web.run_app(self.app, host=self.ip, port=self.port)

if __name__ == "__main__":
    server = Server(ip='127.0.0.1', port=8000)
    server.run()
