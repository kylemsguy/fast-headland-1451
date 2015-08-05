# because Python 2.x is stupid.
from __future__ import division, absolute_import

import os
import uuid
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for

from secret_key import install_secret_key

app = Flask(__name__)
install_secret_key(app)

app.debug = True


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload_apk():
    if request.method == "POST":
        unique_filename = uuid.uuid4().urn[9:] + '.apk'
        f = request.files['File']
        f.save('tmp/' + unique_filename)
        session['last_file'] = unique_filename
        return render_template('file_uploaded.html', filename=unique_filename)
    else:
        return redirect('/', code=302)

@app.route('/getfile/')
def get_uploaded_apk():
    return "Not Implemented"

if __name__ == "__main__":
    app.run()