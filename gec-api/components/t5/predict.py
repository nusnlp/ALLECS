from os.path import join, dirname
import sys

import tensorflow as tf
import tensorflow_text  # Required to run exported model.


def load_predict_fn(model_path):
    if tf.executing_eagerly():
        print("Loading SavedModel in eager mode.")
        imported = tf.saved_model.load(model_path, ["serve"])
        return lambda x: imported.signatures['serving_default'](tf.constant(x))['outputs'].numpy()
    else:
        print("Loading SavedModel in tf 1.x graph mode.")
        tf.compat.v1.reset_default_graph()
        sess = tf.compat.v1.Session()
        meta_graph_def = tf.compat.v1.saved_model.load(sess, ["serve"], model_path)
        signature_def = meta_graph_def.signature_def["serving_default"]
        return lambda x: sess.run(
            fetches=signature_def.outputs["outputs"].name,
            feed_dict={signature_def.inputs["inputs"].name: x}
        )


def load_for_demo(gpu_id=0):
    current_path = join(dirname(__file__))
    model_path = join(current_path, 'models', '')
    physical_devices = tf.config.list_physical_devices('GPU')
    tf.config.set_visible_devices(physical_devices[gpu_id], 'GPU')
    predict_fn = load_predict_fn(model_path)
    return predict_fn


def predict_for_demo(inputs, model):
    if not isinstance(inputs, list):
        inputs = [inputs]
    if len(inputs) > 16:
        print('[WARNING] this model is exported for batch size = 16.' \
                + ' Current batch size is {}'.format(len(inputs)))
    preds = model(inputs)
    return [p.decode('utf-8') for p in preds]

