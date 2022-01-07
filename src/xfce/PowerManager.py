import subprocess


# -- SETTERS
def setBatteryLaptopScreenClosed(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/lid-action-on-battery",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])
def setBatteryScreenOff(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/blank-on-battery",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])
def setBatteryScreenSleep(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/inactivity-on-battery",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])

def setACLaptopScreenClosed(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/lid-action-on-ac",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])
def setACScreenOff(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/blank-on-ac",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])
def setACScreenSleep(value):
    subprocess.call([
        "xfconf-query",
        "-c", "xfce4-power-manager",
        "-p", "/xfce4-power-manager/inactivity-on-ac",
        "-s", str(int(value)),
        "--type", "int",
        "--create"
    ])

# -- GETTERS
def getBatteryLaptopScreenClosed():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/lid-action-on-battery",
        ]).decode("utf-8").rstrip())
    except:
        return 3
    
    return value

def getBatteryScreenOff():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/dpms-on-battery-off",
        ]).decode("utf-8").rstrip())
    except:
        return 60
    
    return value

def getBatteryScreenSleep():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/inactivity-on-battery",
        ]).decode("utf-8").rstrip())
    except:
        return 14
    
    return value

def getACLaptopScreenClosed():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/lid-action-on-ac",
        ]).decode("utf-8").rstrip())
    except:
        return 3
    
    return value

def getACScreenOff():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/dpms-on-ac-off",
        ]).decode("utf-8").rstrip())
    except:
        return 60
    
    return value

def getACScreenSleep():
    try:
        value = int(subprocess.check_output([
            "xfconf-query",
            "-c", "xfce4-power-manager",
            "-p", "/xfce4-power-manager/inactivity-on-ac",
        ]).decode("utf-8").rstrip())
    except:
        return 14
    
    return value
