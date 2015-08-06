import os
import subprocess
from common import UploadedFile


def single_quote(string):
    return "'" + string + "'"


def modify_package_name(upfile_obj):
    # prepare filenames
    filename = "tmp/" + upfile_obj.get_uuid() + ".apk"
    new_foldername = "tmp/output/" + upfile_obj.get_uuid() + "/"
    new_filename = new_foldername + "output" + ".apk"

    os.mkdir(new_foldername)
    os.rename(filename, new_filename)
    # rename the package
    rename_retval = subprocess.call(['ApkRename/apkRename.sh', new_filename, upfile_obj.get_package_name()])
    if rename_retval != 0:
        upfile_obj.set_status(-1)
        raise RuntimeError("subprocess apkRename.sh returned " + str(rename_retval))

    # sign the package
    sign_retval = subprocess.call(['ApkRename/apkSign.sh', new_filename, 'ApkRename/android.keystore'])
    if sign_retval != 0:
        upfile_obj.set_status(-2)
        raise RuntimeError("subprocess apkSign.sh returned " + str(sign_retval))

    upfile_obj.set_status(1)
