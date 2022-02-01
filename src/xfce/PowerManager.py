import subprocess, os


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
            "-p", "/xfce4-power-manager/blank-on-battery",
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
            "-p", "/xfce4-power-manager/blank-on-ac",
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

def isLaptop():
    if os.path.isdir("/proc/pmu"):
        return "Battery" in open("/proc/pmu/info","r").read()
    if os.path.exists("/sys/devices/virtual/dmi/id/chassis_type"):
        type = open("/sys/devices/virtual/dmi/id/chassis_type","r").read().strip()
        return type in ["8", "9", "10", "11"]
    for dev in os.listdir("/sys/class/power_supply"):
        if "BAT" in dev:
            return True
    if os.path.exists("/proc/acpi/battery"):
        return True
    if os.path.isfile("/proc/apm"):
        type = open("/proc/apm","r").read().split(" ")[5]
        return type in ["0xff", "0x80"]
    return False