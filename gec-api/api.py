from os.path import join, dirname
import sys

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

import tensorflow as tf
import tensorflow_text  # Required to run exported model.

from urllib.parse import unquote

import components.gector.predict as gector
import components.t5.predict as t5


app = Flask(__name__)
api = Api(app)

_T5_GPU = 0
_ROBERTA_GPU = 1
_XLNET_GPU = 2

model_gector_roberta = gector.load_for_demo(use_roberta=True, gpu_id=_ROBERTA_GPU)
model_gector_xlnet = gector.load_for_demo(use_roberta=False, gpu_id=_XLNET_GPU)
model_t5_large = t5.load_for_demo(gpu_id=_T5_GPU)


class MODEL(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        model = json_data['model']
        text_input_list = json_data['text_input_list']
        print(f'======INPUT TO {model}=====', flush=True)
        print(text_input_list, sep='\n', flush=True)
        if model == 'GECToR-Roberta':
            text_output_list = gector.predict_for_demo(text_input_list, model_gector_roberta)
        elif model == 'GECToR-XLNet':
            text_output_list = gector.predict_for_demo(text_input_list, model_gector_xlnet)
        elif model == 'T5-Large':
            text_output_list = t5.predict_for_demo(text_input_list, model_t5_large)
        else:
            raise NotImplementedError(f'Model {model} is not recognized.')        
        print(f'======OUTPUT FROM {model}=====', flush=True)
        print(text_output_list, sep='\n', flush=True)
        return jsonify({'model' : model, 'text_output_list' : text_output_list})


api.add_resource(MODEL, "/components/model")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000, use_reloader=False)
