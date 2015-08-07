# because Python 2.x is stupid.
from __future__ import division, absolute_import

# System modules
import uuid
import time

# Flask
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort

# Custom modules
import common
import apkmgr

# Main app instance
app = Flask(__name__)

# Setup
common.install_secret_key(app)
common.generate_keystore()


@app.route('/')
def hello():
    common.clean_current_files()
    return render_template('hello.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload_apk():
    common.clean_current_files()
    if request.method == "POST":
        package_name = request.form['PackageName']
        unique_filename = uuid.uuid4().urn[9:]
        f = request.files['File']
        f.save('tmp/' + unique_filename + '.apk')
        session['last_file'] = unique_filename
        filerec_obj = common.UploadedFile(unique_filename, package_name)
        common.current_files[unique_filename] = filerec_obj
        # spin new thread and run modify_package_name

        return render_template('file_uploaded.html', filename=unique_filename)
    else:
        return redirect('/', code=302)


@app.route('/getfile/')
def get_uploaded_apk():
    common.clean_current_files()
    uuid = request.args.get('uuid')
    if uuid in common.current_files:
        reqfile_obj = common.current_files[uuid]
        # return a json with status code
        return "Not Implemented yet"
    else:
        abort(404)

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
