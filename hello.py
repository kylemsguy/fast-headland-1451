# because Python 2.x is stupid.
from __future__ import division, absolute_import

import os
from flask import Flask
from flask import request
from flask import render_template
from flask import session

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

        f = request.files['the_file']
        f.save('tmp/')

if __name__ == "__main__":
    app.run()