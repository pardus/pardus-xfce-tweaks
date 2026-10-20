#!/usr/bin/python3

import logging

import gi

gi.require_version("Xfconf", "0")
from gi.repository import Xfconf

Xfconf.init()

import pardus_lib_xfce.PowerManager as PowerManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

try:
    timeout = PowerManager.get_blank_screen_timeout()
    logger.info(
        "Configured screen blanking timeout: %d seconds",
        timeout * 60,
    )

    applied = PowerManager.apply_blank_screen_timeout()

    if applied:
        logger.info(
            "X11 screen saver timeout applied: %d seconds",
            timeout * 60,
        )
    else:
        logger.info(
            "X11 screen saver timeout was not changed; "
            "another screen saver is running"
        )

except Exception:
    logger.exception("Failed to apply the X11 screen timeout")

finally:
    PowerManager.close_x11()
