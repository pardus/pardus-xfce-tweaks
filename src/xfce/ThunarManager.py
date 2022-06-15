import subprocess

import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
thunar = Xfconf.Channel.new("thunar")

def restoreDefaultSettings():
    subprocess.run("rm -rf ~/.config/Thunar/*; cp -R /etc/xdg/pardus/Thunar/ ~/.config/Thunar/", shell=True)
    thunar.reset_property("/", True)
