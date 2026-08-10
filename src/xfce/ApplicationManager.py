import subprocess
import shutil
import os
from configparser import ConfigParser
from gi.repository import Gio
from pathlib import Path

STARTUP_PATH = Path(f"{os.environ.get('HOME')}/.config/autostart")
STARTUP_PATH.mkdir(parents=True, exist_ok=True)  # Create if not exists

APPLICATIONS_PATH = os.environ.get("XDG_DATA_DIRS").split(":")
DEFAULT_APPLICATIONS_PATH = f"{os.environ.get('HOME')}/.config/mimeapps.list"
XFCE_DEFAULT_APPLICATIONS_PATH = f"{os.environ.get('HOME')}/.config/xfce4/helpers.rc"

APPLICATIONS = {}


# Startup Applications
def _getApplicationTuple(file):
    name = ""
    icon = ""
    exec = ""
    categories = ""
    try:
        app = Gio.DesktopAppInfo.new_from_filename(file.path)
        if app:
            name = app.get_name()
            icon = (
                app.get_string("Icon")
                if app.get_string("Icon") is not None
                else "image-missing"
            )
            exec = app.get_executable()
            categories = (
                app.get_categories() if app.get_categories() is not None else ""
            )
    except Exception as e:
        print("{}".format(e))
        print("parse_desktopfile error: {} {}".format(file.name, file.path))

    return (exec, name, f"{file.path}", icon, categories)


def get_startup_applications():
    startup_list = []  # [<Gio.DesktopAppInfo>]

    try:
        files = os.scandir(STARTUP_PATH)
        for file in files:
            if file.is_file():
                if file.name.split(".")[-1] == "desktop":
                    print(file.name, "is a startup application")
                    app = Gio.DesktopAppInfo.new_from_filename(file.path)
                    startup_list.append(app)
    except FileNotFoundError as error:
        pass

    return startup_list


# Default Applications
def getApplicationsDictionary():
    applications = {}  # { name: {executable, application file, icon}, ... }

    for p in APPLICATIONS_PATH:
        try:
            files = os.scandir(f"{p}/applications")
            for file in files:
                if file.is_file():
                    if file.name.split(".")[-1] == "desktop":
                        app_tuple = _getApplicationTuple(file)
                        if app_tuple:
                            applications[app_tuple[1]] = {
                                "name": app_tuple[1],
                                "executable": app_tuple[0],
                                "application_file": app_tuple[2],
                                "icon": app_tuple[3],
                                "categories": app_tuple[4],
                            }
        except FileNotFoundError as error:
            continue

    return applications


APPLICATIONS = getApplicationsDictionary()


# webbrowser, filemanager, email. terminalemulator
def getApplicationListFromCategory(category):
    apps = []
    for a in APPLICATIONS:
        app = APPLICATIONS[a]
        if category.lower() in app["categories"].lower():
            apps.append(app)

    return apps


# -- Default XFCE apps: WebBrowser,FileManager,TerminalEmulator,MailReader
def getDefaultXFCEApp(category):
    process = subprocess.run(
        ["xfce4-mime-helper", f"--query={category}"], shell=True, capture_output=True
    )

    binary_file = process.stdout.decode("utf-8").rstrip()

    if category == "MailReader":
        category = "email"

    for a in getApplicationListFromCategory(category):
        if binary_file in a["executable"]:
            return a

    return {"name": ""}


def setDefaultXFCEApp(category, app):
    if not os.path.exists(XFCE_DEFAULT_APPLICATIONS_PATH):
        with open(XFCE_DEFAULT_APPLICATIONS_PATH, "w"):
            pass

    if app == "firefox-esr":
        app = "firefox"

    lines = []
    with open(XFCE_DEFAULT_APPLICATIONS_PATH, "r") as f:
        lines = f.readlines()
        is_category_exists = False
        for i in range(len(lines)):
            if category in lines[i]:
                is_category_exists = True
                lines[i] = f"{category}={app}\n"
                break

        if not is_category_exists:
            lines.append(f"{category}={app}\n")

    with open(XFCE_DEFAULT_APPLICATIONS_PATH, "w") as f:
        for line in lines:
            f.write(line)


def setDefaultApp(key, value):
    if not os.path.exists(DEFAULT_APPLICATIONS_PATH):
        with open(DEFAULT_APPLICATIONS_PATH, "w") as f:
            f.write("[Default Applications]\n")

    conf = ConfigParser(strict=False)
    conf.read(DEFAULT_APPLICATIONS_PATH)

    conf.set("Default Applications", key, value)

    with open(DEFAULT_APPLICATIONS_PATH, "w") as f:
        conf.write(f)


def add_application_to_startup(app_info):
    app_path = app_info.get_filename()
    app_id = app_info.get_id()
    app_new_path = f"{STARTUP_PATH}/{app_id}"

    if not os.path.exists(app_new_path):
        shutil.copy2(app_path, app_new_path)
