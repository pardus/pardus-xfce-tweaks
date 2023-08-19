import subprocess, os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib

LOCALE_CHANGER_PY = os.path.dirname(os.path.abspath(__file__)) + "/locale_changer.py"

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
    # we are using en_US.UTF-8 for lc_ctype
    if ("en_US.UTF-8", "UTF-8") not in langs:
        langs.append(("en_US.UTF-8", "UTF-8"))

    # [(tr_TR.UTF-8, UTF-8), ...]
    return langs

def getDefaultLocale():
    p = subprocess.run(["localectl"], capture_output=True)
    lines = p.stdout.decode("utf-8").splitlines()
    if "LANG=" in lines[0]:
        return lines[0].split("LANG=")[-1].strip()

def startProcess(params, on_exit):
    pid, _, _, _ = GLib.spawn_async(params,
                                        flags=GLib.SPAWN_SEARCH_PATH | GLib.SPAWN_LEAVE_DESCRIPTORS_OPEN | GLib.SPAWN_DO_NOT_REAP_CHILD,
                                        standard_input=False, standard_output=False,
                                        standard_error=False)

    GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, on_exit)

def saveLocaleSettings(locales, default_locale, on_exit):
    print("saveLocaleSettings locales:{} -- defaultlocale{}".format(locales, default_locale))
    # locale should be like this: "tr_TR.UTF-8 UTF-8"
    startProcess(["pkexec", LOCALE_CHANGER_PY, "setlocales", locales, default_locale], on_exit)