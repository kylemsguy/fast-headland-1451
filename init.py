import subprocess


def generate_keystore():
    # generate a keystore using keytool and place it in ApkRename
    p = subprocess.Popen('keytool -genkey -v -keystore ApkRename/android.keystore '
         '-alias alias_name -keyalg RSA -keysize 2048 -validity 10000', stdin=subprocess.PIPE, shell=True)
    p.communicate(b'android\nandroid\nnobody\nnobody\nnobody\nnowhere\nnowhere\nNW\nyes\n')
