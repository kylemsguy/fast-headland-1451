import os
import subprocess
import common
from common import UploadedStatus


def single_quote(string):
    return "'" + string + "'"


def modify_package_name(upfile_obj):
    if upfile_obj.get_status() != UploadedStatus.READY:
        return # what are you even giving me
    upfile_obj.set_status(UploadedStatus.PROCESSING)
    # prepare filenames
    filename = "tmp/" + upfile_obj.get_uuid() + ".apk"
    new_foldername = "tmp/output/" + upfile_obj.get_uuid() + "/"
    new_filename = new_foldername + "output" + ".apk"

    os.mkdir(new_foldername)
    os.rename(filename, new_filename)
    # rename the package
    rename_retval = subprocess.call(['ApkRename/apkRename.sh', new_filename, upfile_obj.get_package_name()])
    if rename_retval != 0:
        upfile_obj.set_status(UploadedStatus.INVALID_FILE)
        # decrease timeout by three hours because reasons
        upfile_obj.set_timeout(upfile_obj.get_timeout() - 3600 * 3)
        raise RuntimeError("subprocess apkRename.sh returned " + str(rename_retval))

    # sign the package
    sign_retval = subprocess.call(['ApkRename/apkSign.sh', new_filename, 'ApkRename/android.keystore'])
    if sign_retval != 0:
        upfile_obj.set_status(UploadedStatus.OTHER_FAILURE)
        raise RuntimeError("subprocess apkSign.sh returned " + str(sign_retval))

    upfile_obj.set_status(UploadedStatus.SUCCESS)
