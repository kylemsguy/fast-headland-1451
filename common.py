import time
import sys
import os
import shutil
import subprocess


class UploadedFile:
    def __init__(self, uuid, package_name):
        self._uuid = uuid
        self._package_name = package_name # new package name
        self._status = 0 # 0 is ready, 1 is success,  -1 is invalid file, -2 is other failure
        self._timeout = time.time() + 3600 * 5 # 5 hour timeout

    def get_uuid(self):
        return self._uuid

    def get_package_name(self):
        return self._package_name

    def get_status(self):
        return self._status

    def get_timeout(self):
        return self._timeout

    def set_timeout(self, timeout):
        self._timeout = timeout

    def set_status(self, status):
        self._status = status

    def get_file(self):
        if self._status == 1:
            return "tmp/output/" + self._uuid + "/" + self._package_name + ".apk"
        elif self._status == 0:
            return None
        elif self._status == -1:
            raise RuntimeError("apkmgr: Invalid File")
        else:
            raise RuntimeError("apkmgr: Other error occurred")


def clean_file(uploaded_file):
    """
    Cleans up old files
    :param uploaded_file: object describing the uploaded file
    :return:whether a file was removed
    """
    if(uploaded_file.get_timeout() <= time.time()):
        uploaded_path = "tmp/" + uploaded_file.get_uuid() + ".apk"
        processed_path = "tmp/output/" + uploaded_file.get_uuid() + "/"
        if os.path.isfile(uploaded_path):
            os.remove(uploaded_path)
        if os.path.isdir(processed_path):
            shutil.rmtree(processed_path)
        return True
    return False


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def generate_keystore():
    # generate a keystore using keytool and place it in ApkRename
    if not os.path.isfile("ApkRename/android.keystore"):
        p = subprocess.Popen('keytool -genkey -v -keystore ApkRename/android.keystore '
             '-alias alias_name -keyalg RSA -keysize 2048 -validity 10000', stdin=subprocess.PIPE, shell=True)
        p.communicate(b'android\nandroid\nnobody\nnobody\nnobody\nnowhere\nnowhere\nNW\nyes\n')


def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.

    """
    filename = os.path.join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        secret_key = os.environ.get('SECRET_KEY')
        if secret_key:
            app.config['SECRET_KEY'] = secret_key
        else:
            print 'Error: No secret key. Create it with:'
            if not os.path.isdir(os.path.dirname(filename)):
                print 'mkdir -p', os.path.dirname(filename)
            print 'head -c 24 /dev/urandom >', filename
            sys.exit(1)