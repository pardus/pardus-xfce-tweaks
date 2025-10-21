#!/usr/bin/env python3
import os
import subprocess
import src.version as Version

from setuptools import setup, find_packages

APPLICATION_FOLDER = "/usr/share/pardus/pardus-xfce-tweaks"


def create_mo_files():
    podir = "po"
    mo = []
    for po in os.listdir(podir):
        if po.endswith(".po"):
            os.makedirs(
                "{}/{}/LC_MESSAGES".format(podir, po.split(".po")[0]), exist_ok=True
            )
            mo_file = "{}/{}/LC_MESSAGES/{}".format(
                podir, po.split(".po")[0], "pardus-xfce-tweaks.mo"
            )
            msgfmt_cmd = "msgfmt {} -o {}".format(podir + "/" + po, mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo.append(
                (
                    "/usr/share/locale/" + po.split(".po")[0] + "/LC_MESSAGES",
                    ["po/" + po.split(".po")[0] + "/LC_MESSAGES/pardus-xfce-tweaks.mo"],
                )
            )
    return mo


data_files = [
    ("/usr/share/applications/", ["tr.org.pardus.xfce-tweaks.desktop"]),
    (APPLICATION_FOLDER, ["pardus-xfce-tweaks.svg"]),
    (
        f"{APPLICATION_FOLDER}/assets",
        ["assets/theme-light.png", "assets/theme-dark.png"],
    ),
    (
        f"{APPLICATION_FOLDER}/src",
        ["src/Main.py", "src/MainWindow.py", "src/version.py"],
    ),
    (
        f"{APPLICATION_FOLDER}/src/xfce",
        [
            "src/xfce/resetall.sh",
        ],
    ),
    (f"{APPLICATION_FOLDER}/ui", ["ui/MainWindow.glade"]),
    (f"{APPLICATION_FOLDER}/css", ["css/style.css"]),
    ("/usr/bin/", ["pardus-xfce-tweaks"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["pardus-xfce-tweaks.svg"]),
    ("/usr/share/polkit-1/actions/", ["tr.org.pardus.xfce-tweaks.policy"]),
] + create_mo_files()

setup(
    name="pardus-xfce-tweaks",
    version=Version.VERSION,
    packages=find_packages(),
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Pardus Developers",
    author_email="dev@pardus.org.tr",
    description="Tweak Pardus XFCE settings",
    license="GPLv3",
    keywords="xfce,tweaks",
    url="https://github.com/pardus/pardus-xfce-tweaks",
)

# os.symlink(f"{APPLICATION_FOLDER}/src/pardus-xfce-tweaks", "/usr/bin/pardus-xfce-tweaks")
