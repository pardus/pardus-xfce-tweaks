#!/usr/bin/python3

import subprocess, sys

def enableLocales(locales):
    # locale should be like this: "tr_TR.UTF-8 UTF-8"

    # disable all locales first:
    subprocess.run("sed -i 's/^ *\\([^#]\\)/# \\1/' /etc/locale.gen", shell=True)

    # remove duplications:
    subprocess.run("awk '!seen[$0]++' /etc/locale.gen | sudo tee /etc/locale.gen", shell=True)

    # enable installed ones:
    subprocess.run("sed -i 's/^# *\\(" + locales + "\\)/\\1/' /etc/locale.gen", shell=True)

def setDefaultLocale(locale):
    # locale should be like this: "tr_TR.UTF-8"
    lc = locale.split(" ")[0]
    subprocess.run(f"localectl set-locale LANG={lc}", shell=True)
    # force lc_ctype to en
    subprocess.run(f"localectl set-locale LC_CTYPE=en_US.UTF-8", shell=True)

def generateLocale():
    subprocess.run("locale-gen")

def saveLocaleSettings(locales, default_locale):
    enableLocales(locales)
    setDefaultLocale(default_locale)
    generateLocale()

if len(sys.argv) > 1:
    if sys.argv[1] == "setlocales":
        saveLocaleSettings(sys.argv[2], sys.argv[3])
    else:
        print("unknown argument error")