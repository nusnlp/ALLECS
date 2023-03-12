# ALLECS: A Lightweight Language Error Correction System (web-interface)

## Installation
1. Clone the repository.
2. Set up a virtual environment (>=Python 3.7).
3. Run `pip install -r requirements.txt`.
4. Modify the `application.secret_key` in `app.wsgi`.
5. Run `python app.py` in the root directory to verify your installation.
6. Optionally, for installation of MEMT, run `git clone https://github.com/kpu/MEMT.git combinations/memt/memt/` to clone the MEMT repository. Then, follow the installation steps in `combinations/memt/memt/install`. ESC can run without additional installation.
7. Configure your web server (Apache, NGINX, etc.) to load and serve ALLECS. We serve ALLECS with mod_wsgi==4.9.4 and Apache 2.4.52. If you want to use mod_wsgi, follow the installation steps in https://pypi.org/project/mod-wsgi/


## GEC model API
The API information for all base models are defined in `config.py`
