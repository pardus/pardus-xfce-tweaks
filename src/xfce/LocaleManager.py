import subprocess
from threading import local

def getAvailableLocales():
    langs = []
    with open("/usr/share/i18n/SUPPORTED", "r") as f:
        for line in f:
            lang, encode_type = line.strip().split(" ")[0:2]
            langs.append((lang, encode_type))
    
    # [(tr_TR.UTF-8, UTF-8), ...]
    return langs


def getInstalledLocales():
    langs = []
    with open("/etc/locale.gen", "r") as f:
        for line in f:
            if line[0] != "#" and len(line) > 3:
                lang, encode_type = line.strip().split(" ")[0:2]
                langs.append((lang, encode_type))
    
    # [(tr_TR.UTF-8, UTF-8), ...]
    return langs


def installLocale(full_locale):
    # locale should be like this: "tr_TR.UTF-8 UTF-8"
    subprocess.run(f"sed -i 's/^# *\({full_locale}\)/\1/' /etc/locale.gen", shell=True)

def removeLocale(full_locale):
    subprocess.run(f"sed -i 's/^\({full_locale}\)/# \1/' /etc/locale.gen", shell=True)

def setDefaultLocale(full_locale):
    # locale should be like this: "tr_TR.UTF-8"
    lc = full_locale.split(" ")[0]
    subprocess.run(f"localectl set-locale LANG={lc}", shell=True)

def generateLocale():
    subprocess.run("pkexec locale-gen")