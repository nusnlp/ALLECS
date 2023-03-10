# ALLECS: A Lightweight Language Error Correction System (gec-api)

This module contains the modified code of [GECToR](https://github.com/grammarly/gector/tree/fea1532608) and a wrapper code of T5 model.

## Installation
1. Clone the repository.
2. Set up a virtual environment (Python >=3.6).
3. Run `pip install -r requirements.txt`.
4. Put the model weight in a folder called `models` in the respective component directory (e.g., `components/gector/models` or `components/t5/models`).
5. Run `python api.py` in the root directory to verify your installation.
6. Serve the api endpoint using Gunicorn or other web servers of personal preferences.

## Adding other base systems
To add other base systems, you need to add the code in the `components` folder and edit `api.py`. 
