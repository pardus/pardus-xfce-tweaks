import os

STARTUP_PATH = f"{os.environ.get('HOME')}/.config/autostart"
APPLICATIONS_PATH = os.environ.get("XDG_DATA_DIRS").split(":")


def _getApplicationTuple(file):
        name = ""
        icon = ""
        with open(file) as f:
            for line in f.readlines():
                if "Name=" in line:
                    name = line.strip().split("=")[1]
                elif "Icon=" in line:
                    icon = line.strip().split("=")[1]
                elif "Type=" in line:
                    if line.strip().split("=")[1] != "Application":
                        return None
                elif "Hidden=" in line:
                    if line.strip().split("=")[1] == "True":
                        return None
                elif name != "" and icon != "":
                    break
        
        return (name, f"{file.path}", icon)

def getStartupTupleList():
    startup_list = [] # [ (name, application file, icon), (name, application file, icon) ... ]

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

def getApplicationTupleList():
    application_list = [] # [ (name, application file, icon), (name, application file, icon) ... ]

    for p in APPLICATIONS_PATH:
        try:
            files = os.scandir( f"{p}/applications" )
            for file in files:
                if file.is_file():
                    if file.name.split(".")[-1] == "desktop":
                        app_tuple = _getApplicationTuple(file)
                        if app_tuple != None:
                            application_list.append(app_tuple)
        except FileNotFoundError as error:
            pass

    return application_list