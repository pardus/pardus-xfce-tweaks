#!/usr/bin/python3

from os import remove
import subprocess, sys

def enableLocales(locales):
    # locale should be like this: "tr_TR.UTF-8 UTF-8"

    # disable all locales first:
    subprocess.run("sed -i 's/^ *\\([^#]\\)/# \\1/' /etc/locale.gen", shell=True)

    # enable installed ones:
    subprocess.run("sed -i 's/^# *\\(" + locales + "\\)/\\1/' /etc/locale.gen", shell=True)

def setDefaultLocale(locale):
    # locale should be like this: "tr_TR.UTF-8"
    lc = locale.split(" ")[0]
    subprocess.run(f"localectl set-locale {lc}", shell=True)

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