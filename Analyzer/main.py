import os
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from keras.models import model_from_json
import static
from multiprocessing import Pipe, Process
import time
from aiohttp import web
import json

cwd = os.getcwd()+"/Static/"
routes = web.RouteTableDef()


class NeuralNetwork(object):
    def __init__(self, file_columns=cwd+'models/enc_columns.txt', file_sclaer = cwd+"models/scaler.save",
                 file_struct =cwd+'models/model1.json', file_weights=cwd+"models/model1.h5"):
        self._file_columns = file_columns
        self._file_scaler = file_sclaer
        self._file_struct = file_struct
        self._file_weights = file_weights
        self._encoded_columns = self._get_saved_columns()
        self._scaler = self._set_scaler()
        self._categories = ["type", "struct_version", 'signature_trusted', 'os', 'flags', 'filetype',
                            'Subsystem', 'Magic', 'Machine', 'FileAlignment', ]
        self.network = self._initialize_nn()

    def _set_scaler(self):
        return joblib.load(self._file_scaler)

    def _initialize_nn(self):
        with open(self._file_struct, 'r') as f:
            loaded_model_json = f.read()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights(self._file_weights)
        #print("Neural network initialized")
        return loaded_model

    def _get_saved_columns(self):
        with open(self._file_columns, 'r') as f:
            return eval(f.readline())

    def predict(self, file):
        pe = static.PortableExecutable(file)
        res = pe.run()
        try:
            assert res != None
        except AssertionError:
            print("Not valid PE file")
            return None

        res = pd.DataFrame([res])

        # Delete unusing features
        res.pop('imports')
        res.pop('peid_signatures')
        # Process None values in signature feature
        res['signature_trusted'] = res['signature_trusted'].fillna(2).astype(np.int64)

        # One-Hot encode
        new_data = pd.get_dummies(res, columns = self._categories)
        new_data = new_data.reindex(columns = self._encoded_columns, fill_value=0)
        new_data = self._scaler.transform(new_data)
        return float(self.network.predict(new_data)[0][0])

    def predict_fromResult(self, res):
        res = pd.DataFrame([res])

        # Delete unusing features
        res.pop('imports')
        res.pop('peid_signatures')
        # Process None values in signature feature
        res['signature_trusted'] = res['signature_trusted'].fillna(2).astype(np.int64)

        # One-Hot encode
        new_data = pd.get_dummies(res, columns = self._categories)
        new_data = new_data.reindex(columns = self._encoded_columns, fill_value=0)
        new_data = self._scaler.transform(new_data)
        return float(self.network.predict(new_data)[0][0])



@routes.view("/analyze")
class Analyze(web.View):
    async def post(self):
        try:
            data = await self.request.json()
            prediction = nn.predict_fromResult(data)
            response_obj = {'prediction': prediction}
            return web.json_response(response_obj)

        except AssertionError:
            return web.HTTPUnauthorized()
        except json.decoder.JSONDecodeError:
            return web.HTTPNoContent()


class AnalyzerServer(object):
    def __init__(self, ip="127.0.0.1", port=4546):
        self.ip = ip
        self.port = port
        self.app = web.Application(middlewares=[])
        self.app.add_routes(routes)

    def run(self):
        print("--- Analyzer is running ---")
        web.run_app(self.app, host=self.ip, port=self.port)



if __name__ == "__main__":
    # nn = NeuralNetwork()
    # print(nn.predict("F:/Downloads/python-3.6.5-amd64.exe"))
    nn = NeuralNetwork()
    analyzer = AnalyzerServer()
    analyzer.run()
