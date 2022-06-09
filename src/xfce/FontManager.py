import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
xsettings = Xfconf.Channel.new("xsettings")

def getSystemFont():
    return xsettings.get_string("/Gtk/FontName", "")

def getMonospaceFont():
    return xsettings.get_string("/Gtk/MonospaceFontName", "")

def setSystemFont(font):
    xsettings.set_string("/Gtk/FontName", font)

def setMonospaceFont(font):
    xsettings.set_string("/Gtk/MonospaceFontName", font)