import os

import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
xfce4_power_manager = Xfconf.Channel.new("xfce4-power-manager")

# -- SETTERS
def setBatteryLaptopScreenClosed(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/lid-action-on-battery", int(value))
    
def setBatteryScreenOff(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/blank-on-battery", int(value))

def setBatteryScreenSleep(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/inactivity-on-battery", int(value))

def setACLaptopScreenClosed(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/lid-action-on-ac", int(value))

def setACScreenOff(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/blank-on-ac", int(value))

def setACScreenSleep(value):
    xfce4_power_manager.set_int("/xfce4-power-manager/inactivity-on-ac", int(value))

# -- GETTERS
def getBatteryLaptopScreenClosed():
    return xfce4_power_manager.get_int("/xfce4-power-manager/lid-action-on-battery", 3)

def getBatteryScreenOff():    
    return xfce4_power_manager.get_int("/xfce4-power-manager/blank-on-battery", 60)

def getBatteryScreenSleep():
    return xfce4_power_manager.get_int("/xfce4-power-manager/inactivity-on-battery", 14)

def getACLaptopScreenClosed():    
    return xfce4_power_manager.get_int("/xfce4-power-manager/lid-action-on-ac", 3)

def getACScreenOff():    
    return xfce4_power_manager.get_int("/xfce4-power-manager/blank-on-ac", 60)

def getACScreenSleep():    
    return xfce4_power_manager.get_int("/xfce4-power-manager/inactivity-on-ac", 14)

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