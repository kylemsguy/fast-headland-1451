import time
import sys
import os


class UploadedFile:
    def __init__(self, uuid, package_name):
        self._uuid = uuid
        self._package_name = package_name
        self._status = 0 # 0 is ready, 1 is success,  -1 is invalid file, -2 is other failure
        self._timeout = time.time() + 3600 * 5 # 5 hour timeout

    def get_uuid(self):
        return self._uuid

    def get_status(self):
        return self._status

    def get_timeout(self):
        return self._timeout

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