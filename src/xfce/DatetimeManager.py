import os, subprocess
import shutil
from time import sleep

# PATHS
HOME_PATH = os.environ.get('HOME', None)
PLUGIN_RC_FILE_DIRECTORY = f"{HOME_PATH}/.config/xfce4/panel/"
PLUGIN_RC_FILE_PATH = f"{HOME_PATH}/.config/xfce4/panel/datetime-8.rc"
ETC_XDG_DATETIME_PATH = "/etc/xdg/pardus/xfce4/panel/datetime-8.rc"

# Copy the default config file if not exists:
if not os.path.exists(PLUGIN_RC_FILE_PATH):
    # Create directories if not exists
    os.makedirs(PLUGIN_RC_FILE_DIRECTORY, exist_ok=True)

    shutil.copyfile(ETC_XDG_DATETIME_PATH, PLUGIN_RC_FILE_PATH)

# Read config file
configFileData = ""
with open(PLUGIN_RC_FILE_PATH, 'r') as file:
    configFileData = file.read()


def get(key):
    global configFileData

    lines = configFileData.splitlines()
    for i in range(len(lines)):
        if key in lines[i]:
            return lines[i].split("=")[-1]
    
    return None

def set(key, value):
    global configFileData

    lines = configFileData.splitlines()
    is_key_exists = False
    for i in range(len(lines)):
        if key in lines[i]:
            lines[i] = f"{key}={value}"
            is_key_exists = True
            break
    
    if not is_key_exists:
        lines.append(f"{key}={value}")
    
    configFileData = "\n".join(lines)

def saveFile():
    global configFileData
    
    subprocess.run("xfce4-panel -q", shell=True)

    sleep(0.5)

    with open(PLUGIN_RC_FILE_PATH, 'w') as file:
        file.write(configFileData)
    
    subprocess.run("xfce4-panel &", shell=True)

def restoreDefaultSettings():
    os.remove(PLUGIN_RC_FILE_PATH)
    shutil.copyfile(ETC_XDG_DATETIME_PATH, PLUGIN_RC_FILE_PATH)