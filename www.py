import os
import random

from flask import Flask
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

import asciipy

app = Flask(__name__)


def randstr(length):
    strset = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join([random.choice(strset) for _ in range(length)])


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload_handler():
    flask_file = request.files['file']
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(flask_file.filename))
    flask_file.save(input_path)

    output = asciipy.start(input_path, thumbnail_resolution=(240, 240), callback=None)
    return render_template('output.html', output=output)

app.config['UPLOAD_FOLDER'] = '/tmp/asciipy'
app.run(host='0.0.0.0')
