#!/usr/bin/python3

import sys
import pardus_lib_xfce.LocaleManager as LocaleManager


if len(sys.argv) > 1:
    if sys.argv[1] == "setlocales":
        LocaleManager.save_locale_settings(sys.argv[2], sys.argv[3])
    else:
        print("unknown argument error")
