import time
import sys
import os
import shutil
import subprocess
import threading
from enum import IntEnum

# Global variables
current_files = {}
cleanup_thread = None
last_cleanup = 0

# Mutexes
current_files_mutex = threading.Lock()


class UploadedStatus(IntEnum):
    READY = 0
    PROCESSING = 1
    SUCCESS = 2

    # failure codes are all negative
    INVALID_FILE = -1
    OTHER_FAILURE = -2


class UploadedFile:
    def __init__(self, uuid, package_name):
        self._uuid = uuid
        self._package_name = package_name  # new package name
        self._status = UploadedStatus.READY
        self._timeout = time.time() + 3600 * 5  # 5 hour timeout
        self._worker = None

    def get_worker(self):
        return self._worker

    def get_uuid(self):
        return self._uuid

    def get_package_name(self):
        return self._package_name

    def get_status(self):
        return self._status

    def get_timeout(self):
        return self._timeout

    def set_worker(self, worker):
        self._worker = worker

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


def start_cleanup():
    global cleanup_thread
    global last_cleanup
    if cleanup_thread and cleanup_thread.is_alive():
        return # already another thread running
    elif last_cleanup < time.time() - 1800:
        cleanup_thread = start_threaded(clean_current_files)


def clean_current_files():
    """
    Garbage collection for old files or if running out of memory
    NOTE: Should only be called in a thread
    :return:Nothing
    """
    current_files_mutex.acquire(True)
    global last_cleanup
    last_cleanup = time.time()
    try:
        for key in current_files.keys():
            if clean_file(current_files[key]):
                current_files.pop(key)

        if get_size('tmp') > 1024 * 1024 * 200:  # 200MB
            # TEMPORARY: ABORT ABORT ABORT
            for key in current_files.keys():
                current_files[key].set_timeout(time.time() - 1)
                clean_file(current_files[key])
                current_files.pop(key)
    except Exception as e:
        print "clean_current_files: " + e
    finally:
        current_files_mutex.release()


def clean_file(uploaded_file):
    """
    Cleans up old files, but does not remove the entry from memory
    :param uploaded_file: object describing the uploaded file
    :return:whether a file was removed
    """
    if (uploaded_file.get_timeout() <= time.time()):
        uploaded_path = "tmp/" + uploaded_file.get_uuid() + ".apk"
        processed_path = "tmp/output/" + uploaded_file.get_uuid() + "/"
        if uploaded_file.get_status() == UploadedStatus.READY:
            try:
                os.remove(uploaded_path)
            except OSError as e:
                print "clean_file: Unable to delete uploaded file: " + e
        else:
            try:
                shutil.rmtree(processed_path)
            except OSError as e:
                print "clean_file: Unable to delete uploaded file: " + e
        return True
    return False


def start_threaded(func, *args):
    thread = threading.Thread(target=func, args=args)
    thread.start()
    return thread

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
        p = subprocess.Popen('keytool -genkey -v -keystore ApkRename/android.keystore ' +
                             '-alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000',
                             stdin=subprocess.PIPE, shell=True)
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
            print 'Or specify the key with the SECRET_KEY environment variable.'
            sys.exit(1)
