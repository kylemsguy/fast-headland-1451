# because Python 2.x is stupid.
from __future__ import division, absolute_import

import uuid
import time

from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort

from common import install_secret_key
from common import UploadedFile
from common import generate_keystore
from common import clean_file
from common import get_size

# Global variables
current_files = {}

# Main app instance
app = Flask(__name__)

# Setup
install_secret_key(app)
generate_keystore()


def clean_current_files():
    for key in current_files.keys():
        if clean_file(current_files[key]):
            current_files.pop(key)

    if get_size('tmp') > 1024 * 1024 * 200: # 200MB
        # TEMPORARY: ABORT ABORT ABORT
        for key in current_files.keys():
            current_files[key].set_timeout(time.time() - 1)
            clean_file(current_files[key])
            current_files.pop(key)



@app.route('/')
def hello():
    clean_current_files()
    return render_template('hello.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload_apk():
    clean_current_files()
    if request.method == "POST":
        package_name = request.form['PackageName']
        unique_filename = uuid.uuid4().urn[9:]
        f = request.files['File']
        f.save('tmp/' + unique_filename + '.apk')
        session['last_file'] = unique_filename
        filerec_obj = UploadedFile(unique_filename, package_name)
        current_files[unique_filename] = filerec_obj
        # spin new thread and run modify_package_name

        return render_template('file_uploaded.html', filename=unique_filename)
    else:
        return redirect('/', code=302)


@app.route('/getfile/')
def get_uploaded_apk():
    clean_current_files()
    uuid = request.args.get('uuid')
    if uuid in current_files:
        reqfile_obj = current_files[uuid]
        # get status code and return it or link to file if found
        return "Not Implemented yet"
    else:
        abort(404)

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
