#!/usr/bin/env python3
from setuptools import setup, find_packages
from shutil import copyfile
import os

APPLICATION_FOLDER="/usr/share/pardus/pardus-xfce-tweaks"

data_files = [
    ("/usr/share/applications/", ["tr.org.pardus.xfce-tweaks.desktop"]),
    ("/usr/share/locale/tr/LC_MESSAGES/", ["translations/tr/LC_MESSAGES/pardus-xfce-tweaks.mo"]),
    (APPLICATION_FOLDER, ["pardus-xfce-tweaks.svg"]),
    (f"{APPLICATION_FOLDER}/src", ["src/main.py", "src/MainWindow.py"]),
    (f"{APPLICATION_FOLDER}/ui", ["ui/MainWindow.glade"]),
    #("/usr/bin/", ["pardus-xfce-tweaks"]),
    ("/usr/share/icons/hicolor/scalable/apps/", ["pardus-xfce-tweaks.svg"])
]

setup(
    name="pardus-xfce-tweaks",
    version="0.1.0",
    packages=find_packages(),
    scripts=["pardus-xfce-tweaks"],
    install_requires=["PyGObject"],
    data_files=data_files,
    author="Pardus Altyapı",
    author_email="altyapi@pardus.org.tr",
    description="Pardus XFCE Tweaks %SHORT_DESCRIPTION% Configurations",
    license="GPLv3",
    keywords="",
    url="https://www.pardus.org.tr",
)

os.symlink(f"{APPLICATION_FOLDER}/src/main.py", "/usr/bin/pardus-xfce-tweaks")
