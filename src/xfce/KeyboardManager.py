import subprocess

import gi
gi.require_version('Xfconf', '0')
from gi.repository import Xfconf


keyboards = {"tr-":False, "tr-f":False, "us-":False}

keyboardPlugin = ""

Xfconf.init()
keyboard_layout = Xfconf.Channel.new("keyboard-layout")
xfce4_panel = Xfconf.Channel.new("xfce4-panel")

def initializeSettings():
    # Add Super + Space combination to change layouts
    keyboard_layout.set_string("/Default/XkbOptions/Group", "grp:win_space_toggle")

    # Get system settings if disabled
    useSystemKeyboard = keyboard_layout.get_bool("/Default/XkbDisable", False)

    if useSystemKeyboard:
        get_system_keyboards()
        set_keyboard_state()

def set_keyboard_state():
    layouts = []
    variants = []

    for key, value in keyboards.items():
        layout, variant = key.split("-")
        
        if value:
            layouts.append(layout)
            variants.append(variant)
        else:
            layouts.append("")
            variants.append("")

    keyboard_layout.set_string("/Default/XkbLayout", ",".join(layouts))
    keyboard_layout.set_string("/Default/XkbVariant", ",".join(variants))
    keyboard_layout.set_bool("/Default/XkbDisable", False)

# Add Keyboard Layouts:
def setTurkishQ(state):
    keyboards["tr-"] = state
    set_keyboard_state()

def setTurkishF(state):
    keyboards["tr-f"] = state
    set_keyboard_state()

def setEnglish(state):
    keyboards["us-"] = state
    set_keyboard_state()

# Get System's Keyboard
def get_system_keyboards():
    global keyboards

    layoutProcess = subprocess.run("cat /etc/default/keyboard | grep XKBLAYOUT | tr -d '\"'", shell=True, capture_output=True)
    variantProcess = subprocess.run("cat /etc/default/keyboard | grep XKBVARIANT | tr -d '\"'", shell=True, capture_output=True)
    
    layouts = layoutProcess.stdout.decode("utf-8").rstrip().split("=")[1].split(",")
    variants = variantProcess.stdout.decode("utf-8").rstrip().split("=")[1].split(",")

    for i in range(len(layouts)):
        key = layouts[i] + "-" + variants[i]
        if key in keyboards:
            keyboards[key] = True

    return keyboards

# Get Current Keyboard State
def getKeyboardState():
    global keyboards

    layouts = keyboard_layout.get_string("/Default/XkbLayout", "")
    variants = keyboard_layout.get_string("/Default/XkbVariant", "")

    if layouts == "" or variants == "":
        get_system_keyboards()
        set_keyboard_state()

        return keyboards

    layouts = layouts.split(",")
    variants = variants.split(",")

    for i in range(len(layouts)):
        key = layouts[i] + "-" + variants[i]
        if key in keyboards:
            keyboards[key] = True
    
    return keyboards


# PLUGIN:
def createKeyboardPlugin():
    # Add keyboard
    subprocess.call([
        "xfce4-panel",
        "--add=xkb"
    ])

    getKeyboardPlugin()
    changeKeyboardPluginPlacement()
    
    # Display Language Name (not country)
    xfce4_panel.set_int(f"/plugins/{keyboardPlugin}/display-name", 1)

    # Display text (not flag)
    xfce4_panel.set_int(f"/plugins/{keyboardPlugin}/display-type", 2)

    # Enable globally (not program-wide)
    xfce4_panel.set_int(f"/plugins/{keyboardPlugin}/group-policy", 0)

def removeKeyboardPlugin():
    # Remove plugin
    xfce4_panel.reset_property(f"/plugins/{keyboardPlugin}", True)

    # Refresh panel
    subprocess.call([
        "xfce4-panel",
        "-r"
    ])


def getKeyboardPlugin():
    global keyboardPlugin

    for key, value in xfce4_panel.get_properties("/plugins").items():
        if type(value) is str and "xkb" in value:
            keyboardPlugin = key.split("/")[2]
            return keyboardPlugin
    
    return ""

def changeKeyboardPluginPlacement():
    pluginList = xfce4_panel.get_arrayv("/panels/panel-1/plugin-ids")
    
    if int(keyboardPlugin.split("-")[1]) == pluginList[-2]:
        return
    
    
    pluginList[-1], pluginList[-2] = pluginList[-2], pluginList[-1]
    

    setArrayCommand = []
    for i in range(len(pluginList)):
        setArrayCommand.append("-t")
        setArrayCommand.append("int")

    for i in range(len(pluginList)):
        setArrayCommand.append("-s")
        setArrayCommand.append(pluginList[i])
    
    xfce4_panel.set_arrayv("/panels/panel-1/plugin-ids", pluginList)

    subprocess.call([
        "xfce4-panel",
        "-r"
    ])