from flask import Flask
import os

app = Flask(__name__)
from app import views

if os.environ.get('DYNO') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')