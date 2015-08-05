import os
from androguard.core.bytecodes.apk import APK
from common import UploadedFile


def modify_package_name(upfile_obj, default_path="tmp/"):
    # TODO: check if upfile_obj is an UploadedFile or just a path
    assert isinstance(upfile_obj, UploadedFile)
    # construct path to APK and get APK object
    apk_path = default_path + upfile_obj.get_uuid() + ".apk"
    apk_obj = APK(apk_path)

    if not apk_obj.is_valid_APK():
        upfile_obj.set_status(-1)
        os.remove(apk_path)
        return

    # modify AndroidManifest.xml
    manifest_xml = apk_obj.get_AndroidManifest()
    manifest_element = manifest_xml.documentElement
    manifest_element.setAttribute('package', upfile_obj.get_package_name())



