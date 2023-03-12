from os import listdir, makedirs
from os.path import join, dirname
from shutil import rmtree
import subprocess

# inference for demo
def predict(data):
    exp_dir = 'exp/bea-exp'  # using BEA-2019
    if 'GECToR-Roberta' in data:
        exp_dir += '-1'
    if 'GECToR-XLNet' in data:
        exp_dir += '-2'
    if 'T5-Large' in data:
        exp_dir += '-3'

    combination_path = join(dirname(__file__), exp_dir, '')
    for combination, predictions in data.items():
        with open(join(combination_path, f'{combination}.txt'), 'w', encoding='utf-8') as out:
            for prediction in predictions:
                out.write(prediction + "\n")
    
    subprocess.call("./test.sh", cwd=combination_path, shell=True)

    with open(join(combination_path, 'matched.1best'), 'r', encoding='utf-8') as final_out:
        sentences = final_out.readlines()

    return sentences
