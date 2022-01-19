import subprocess

def getSystemFont():
    try:
        font = subprocess.check_output([
                "xfconf-query",
                "-c", "xsettings",
                "-p", "/Gtk/FontName",
            ]).decode("utf-8").rstrip()
        return font
    except:
        return ""

def getMonospaceFont():
    try:
        font = subprocess.check_output([
                "xfconf-query",
                "-c", "xsettings",
                "-p", "/Gtk/MonospaceFontName",
            ]).decode("utf-8").rstrip()
        return font
    except:
        return ""

def setSystemFont(font):
    subprocess.call([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Gtk/FontName",
        "-s", font,
        "--type", "string",
        "--create"
    ])

def setMonospaceFont(font):
    subprocess.call([
        "xfconf-query",
        "-c", "xsettings",
        "-p", "/Gtk/MonospaceFontName",
        "-s", font,
        "--type", "string",
        "--create"
    ])