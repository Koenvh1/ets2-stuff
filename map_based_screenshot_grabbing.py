#!/usr/bin/env python3
#
# This script tries to grab a bunch of screenshots by moving a draggable area
# around.
#
# Partly inspired by http://forum.scssoft.com/viewtopic.php?p=405122#p405122
#
# Tools for automating mouse/keyboard:
# * xdotool - http://www.semicomplete.com/projects/xdotool/xdotool.xhtml https://github.com/jordansissel/xdotool
# * PyUserInput - https://github.com/SavinaRoja/PyUserInput
# * pyautogui - https://github.com/asweigart/pyautogui
# * autopy - https://github.com/msanders/autopy
#
# Other tools:
# * pyewmh (X11-only) - https://github.com/parkouss/pyewmh.git
# * import (from ImageMagick) - http://www.imagemagick.org/script/import.php
#
# TODO: Rename this script to something more sensible.

import re
import subprocess
import time

# Note: python-xlib automatically prints the following line:
# <class 'Xlib.protocol.request.QueryExtension'>
# Look at this bug report: https://bugs.launchpad.net/listen/+bug/561707

# Cross-platform.
from pymouse import PyMouse
mouse = PyMouse()

# For querying and manipulating the window.
# X11-only, essentially Linux-only.
from ewmh import EWMH
ewmh = EWMH()


def get_win_name(win):
    return ewmh.getWmVisibleName(win) or ewmh.getWmName(win) or ''


def get_win_frame(win):
    # https://stackoverflow.com/questions/12775136/get-window-position-and-size-in-python-with-xlib
    while win.query_tree().parent != ewmh.root:
        win = win.query_tree().parent
    return win


def get_win_geometry(win):
    # https://stackoverflow.com/questions/12775136/get-window-position-and-size-in-python-with-xlib
    return get_win_frame(win).get_geometry()


def get_Google_Maps_window():
    windows = [
        w for w in ewmh.getClientList()
        if re.match(r'^Google Maps.*Google Chrome$', get_win_name(w))
    ]
    if len(windows) == 0:
        raise RuntimeError('Google Chrome window with Google Maps was not found.')
    if len(windows) > 1:
        raise RuntimeError('Multiple Google Chrome + Google Maps windows were found.')
    return windows[0]


def grab_screenshot(win, offset_x, offset_y):
    filename = 'google_map_x={0}_y={1}.tif'.format(offset_x, offset_y)
    subprocess.check_call(['import', '-window', str(win.id), filename])


def main():
    # Grabbing Google Maps screenshots from Chrome browser.
    win = get_Google_Maps_window()
    geom = get_win_geometry(win)

    # "Safe" borders:
    margin_left = 120
    margin_right = 70
    margin_top = 160  # Around 90px of Chrome title+location+bookmarks, plus 70px of actual Google Maps.
    margin_bottom = 60

    min_x = geom.x + margin_left
    max_x = geom.x + geom.width - margin_right
    min_y = geom.y + margin_top
    max_y = geom.y + geom.height - margin_bottom

    mid_x = (min_x + max_x) // 2
    mid_y = (min_y + max_y) // 2
    size_x = (max_x - min_x)
    size_y = (max_y - min_y)

    ewmh.setActiveWindow(win)
    ewmh.display.flush()

    offset_x = 0
    offset_y = 0
    repeat_x = 3
    repeat_y = 3
    direction = 1
    for i in range(repeat_y):
        for j in range(repeat_x):
            start_x = mid_x + (size_x * direction) // 2
            delta_x = size_x * direction

            mouse.move(start_x, mid_y)
            time.sleep(0.5)
            grab_screenshot(win, offset_x, offset_y)
            mouse.drag(start_x - delta_x, mid_y)
            offset_x += delta_x
            time.sleep(0.5)

        direction *= -1
        mouse.move(mid_x, max_y)
        time.sleep(0.5)
        mouse.drag(mid_x, max_y - size_y)
        offset_y += size_y
        time.sleep(0.5)


if __name__ == '__main__':
    main()
