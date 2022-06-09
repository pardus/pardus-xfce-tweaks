import os, pwd

import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
xsettings = Xfconf.Channel.new("xsettings")
xfwm4 = Xfconf.Channel.new("xfwm4")

USER = pwd.getpwuid(os.getuid()).pw_name

themePath = ["/usr/share/themes/", f"/home/{USER}/.themes/"]

def getThemeList():
    themes = []
    windowThemes = []

    for path in themePath:
        try:
            files = os.scandir( path )
            for file in files:
                if file.is_dir():
                    themes.append(file.name)
                    
                    if os.path.isdir(f"{path}/{file.name}/xfwm4"):
                        windowThemes.append(file.name)
        except FileNotFoundError as error:
            pass
    
    themes.sort()
    windowThemes.sort()
    return [themes, windowThemes]

def setTheme(theme):
    xsettings.set_string("/Net/ThemeName", theme)

def setWindowTheme(theme):
    xfwm4.set_string("/general/theme", theme)

def setIconTheme(theme):
    xsettings.set_string("/Net/IconThemeName", theme)

def getTheme():
    return xsettings.get_string("/Net/ThemeName", "")

def getWindowTheme():
    return xfwm4.get_string("/general/theme", "")

def getIconTheme():
    return xsettings.get_string("/Net/IconThemeName", "")