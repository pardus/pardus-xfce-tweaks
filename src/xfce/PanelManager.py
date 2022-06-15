import subprocess

import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf

Xfconf.init()
xfce4_panel = Xfconf.Channel.new("xfce4-panel")

plugin = ""
items = []

def _get_actions_plugin():
    global plugin
    if plugin != "": return

    for key,value in xfce4_panel.get_properties("/plugins").items():
        if type(value) is str and "actions" in value:
            plugin = key
            return

def getActionsItems():
    global items
    _get_actions_plugin()

    items = xfce4_panel.get_string_list(f"{plugin}/items")
    items_obj = {'lock-screen': False, 'switch-user': False, 'separator': False, 'suspend': False, 'hibernate': False, 'shutdown': False, 'restart': False, 'logout': True, 'logout-dialog': False, 'hybrid-sleep': False}
    
    for i in items:
        key, value = i[1:], True if i[0] == "+" else False
        items_obj[key] = value
    
    return items_obj

def setActionsItem(key, value):
    # key = 'restart', 'shutdown'
    # value = '+' or '-'
    global items

    items = xfce4_panel.get_string_list(f"{plugin}/items")

    changed = False
    for i in range(len(items)):
        if key == items[i][1:]:
            items[i] = f"{value}{key}"
            changed = True
            break
    
    if not changed:
        items.append(f"{value}{key}")
    
    xfce4_panel.set_arrayv(f"{plugin}/items", items)

def restoreActionsDefault():
    global items
    items = ['-lock-screen', '-switch-user', '-separator', '-suspend', '-hibernate', '-separator', '-shutdown', '-restart', '-separator', '+logout', '-logout-dialog', '-hybrid-sleep']

    xfce4_panel.set_arrayv(f"{plugin}/items", items)

def restoreDefaultSettings():
    xfce4_panel.reset_property("/", True)
    subprocess.run("""xfce4-panel --quit;
        pkill xfconfd;
        rm -rf ~/.config/xfce4/panel/* ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
        cp -R /etc/xdg/pardus/xfce4/panel/* ~/.config/xfce4/panel/;
        cp /etc/xdg/pardus/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml;
        (xfce4-panel &)""", shell=True)