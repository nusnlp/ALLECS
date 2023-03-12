import logging
import sys
import os

logging.basicConfig(stream=sys.stderr)

os.environ["LANG"] = "en_US.UTF-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LC_CTYPE"] = "en_US.UTF-8"
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from app import app as application

application.secret_key = 'your_secret_key'
