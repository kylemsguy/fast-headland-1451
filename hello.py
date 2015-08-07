# because Python 2.x is stupid.
from __future__ import division, absolute_import

# System modules
import uuid

# Flask
from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort
from flask import send_from_directory
from flask import jsonify

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
    common.start_cleanup()
    return render_template('hello.html')


@app.route('/upload/', methods=['GET', 'POST'])
def upload_apk():
    common.start_cleanup()
    if request.method == "POST":
        package_name = request.form['PackageName']
        unique_filename = uuid.uuid4().urn[9:]
        f = request.files['File']
        f.save('tmp/' + unique_filename + '.apk')
        session['last_file'] = unique_filename
        # perhaps try to lock mutex?
        filerec_obj = common.UploadedFile(unique_filename, package_name)
        common.current_files[unique_filename] = filerec_obj
        # spin new thread and run modify_package_name
        common.start_threaded(apkmgr.modify_package_name, filerec_obj)
        return render_template('file_uploaded.html', filename=unique_filename)
    else:
        return redirect('/', code=302)


@app.route('/status/')
def get_uploaded_apk():
    common.start_cleanup()
    uuid = request.args.get('uuid')
    if uuid in common.current_files:
        reqfile_obj = common.current_files[uuid]
        # return a json with status code
        retdata = {'status': reqfile_obj.get_status().value}
        if reqfile_obj.get_status() == common.UploadedStatus.SUCCESS:
            retdata['url'] = "/getfile/" + reqfile_obj.get_uuid() + ".apk"
        else:
            retdata['url'] = ""

        return jsonify(**retdata)
    else:
        abort(404)


@app.route('/getfile/<uuid>.apk')
def send_file(uuid):
    # sending as uuid because too lazy to translate to filename
    common.start_cleanup()
    if uuid in common.current_files:
        reqfile_obj = common.current_files[uuid]
        if reqfile_obj.get_status() != common.UploadedStatus.SUCCESS:
            abort(404)
        else:
            directory = "tmp/output/" + reqfile_obj.get_uuid() + "/"
            filename =  "output.apk"
            return send_from_directory(directory, filename)

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
