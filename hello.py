# because Python 2.x is stupid.
from __future__ import division, absolute_import

import uuid
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect

from common import install_secret_key
from common import UploadedFile

# Global variables
current_files = {}

# Main app instance
app = Flask(__name__)
install_secret_key(app)


@app.route('/')
def hello():
    return render_template('hello.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload_apk():
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
    pass

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
