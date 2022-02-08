from ast import Break
import subprocess
import os
from configparser import ConfigParser

STARTUP_PATH = f"{os.environ.get('HOME')}/.config/autostart"
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
        with open(file) as f:
            for line in f.readlines():
                line = line.rstrip()
                
                try:
                    key = line[:line.index("=")]
                    value = line[line.index("=")+1:]

                    if "Name" == key:
                        name = value
                    elif "Icon" == key:
                        icon = value
                    elif "Categories" == key:
                        categories = value
                    elif "Exec" == key:
                        exec = value.split(" ")[0].split("/")[-1].split(" ")[0]
                    elif "Type" == key:
                        if value.lower() != "application":
                            return None
                    elif "Hidden" == key or "NoDisplay" == key:
                        if value.lower() == "true":
                            return None
                    elif name != "" and icon != "" and exec != "" and categories != "":
                        break
                except:
                    pass
        
        return (exec, name, f"{file.path}", icon, categories)

def getStartupTupleList():
    startup_list = [] # [ (executable, name, application file, icon, categories), ... ]

    try:
        files = os.scandir( STARTUP_PATH )
        for file in files:
            if file.is_file():
                if file.name.split(".")[-1] == "desktop":
                    app_tuple = _getApplicationTuple(file)
                    if app_tuple != None:
                        startup_list.append(app_tuple)
    except FileNotFoundError as error:
        pass

    return startup_list


# Default Applications
def getApplicationsDictionary():
    applications = {} # { name: {executable, application file, icon}, ... }

    for p in APPLICATIONS_PATH:
        try:
            files = os.scandir( f"{p}/applications" )
            for file in files:
                if file.is_file():
                    if file.name.split(".")[-1] == "desktop":
                        app_tuple = _getApplicationTuple(file)
                        if app_tuple != None:
                            applications[app_tuple[1]] = {"name":app_tuple[1], "executable":app_tuple[0], "application_file":app_tuple[2], "icon":app_tuple[3], "categories":app_tuple[4]}
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
    process = subprocess.run(f"xfce4-mime-helper --query={category}", shell=True, capture_output=True)
    
    binary_file = process.stdout.decode("utf-8").rstrip()

    if category == "MailReader":
        category = "email"
    
    for a in getApplicationListFromCategory(category):
        if binary_file in a["executable"]:
            return a
    
    return {"name":""}

def setDefaultXFCEApp(category, app):
    if not os.path.exists(XFCE_DEFAULT_APPLICATIONS_PATH):
        with open(XFCE_DEFAULT_APPLICATIONS_PATH, 'w'): pass

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
        with open(DEFAULT_APPLICATIONS_PATH, 'w') as f:
            f.write("[Default Applications]\n")

    conf = ConfigParser(strict=False)
    conf.read(DEFAULT_APPLICATIONS_PATH)

    conf.set("Default Applications", key, value)

    with open(DEFAULT_APPLICATIONS_PATH, "w") as f:
        conf.write(f)