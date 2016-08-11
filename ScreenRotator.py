#!/usr/bin/env python3

import os
import signal
from subprocess import call , check_output
from gi.repository import Gtk
from gi.repository import AppIndicator3 as AppIndicator

APPINDICATOR_ID = "screenrotator"


# Adding ASUS T100 TA Vars ...

XRANDROUT="DSI1"

cmd = r"""xinput --list | grep SIS | sed 's/.*id=\([0-9]*\).*/\1/'; xinput --list | grep "ASUS.*Base.*pointer" | sed 's/.*id=\([0-9]*\).*/\1/'"""
INDEVS = check_output( cmd , shell=True ).decode().split("\n")
INDEVS.pop()

cmd = r"""xrandr -q --verbose | grep DSI1 | cut -d" " -f6"""


NEW_ROT="normal"

ACC_X = check_output('cat /sys/bus/iio/devices/iio\:device0/in_accel_x_raw', shell=True).decode().replace("\n","")
ACC_Y = check_output('cat /sys/bus/iio/devices/iio\:device0/in_accel_y_raw', shell=True).decode().replace("\n","")

#END OF VARS

def main():
    indicator = AppIndicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('./icon.svg'), AppIndicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    Gtk.main()

def build_menu():
    menu = Gtk.Menu()
    #brightness
    item_brightness_up = Gtk.MenuItem('Increase Brightness')
    item_brightness_up.connect('activate', increase_brightness)
    menu.append(item_brightness_up)
    item_brightness_down = Gtk.MenuItem("Decrease Brightness")
    item_brightness_down.connect('activate', decrease_brightness)
    menu.append(item_brightness_down)
    #Landscape
    item_rotate = Gtk.MenuItem('Rotate Screen')
    item_rotate.connect('activate', rotate_screen)
    menu.append(item_rotate)
     
    #seperator
    seperator = Gtk.SeparatorMenuItem()
    menu.append(seperator)
    #quit
    item_quit = Gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu

def rotate_screen(source):
    orientation = check_output( cmd , shell=True ).decode().replace("\n","")
    if orientation == "normal" :
        direction = "left"
        CTM = ["0","-1","1","1","0","0","0","0","1"]
    else :
        direction = "normal"
        CTM = ["1","0","0","0","1","0","0","0","1"]
    call(["xrandr","--output",XRANDROUT, "--rotate",direction])
    for i in INDEVS :
        call(["xinput","set-prop",i,'Coordinate Transformation Matrix']+CTM)


def increase_brightness(source):
    call(["xbacklight", "-inc", "20"])

def decrease_brightness(source):
    call(["xbacklight", "-dec", "20"])

if __name__ == "__main__":
    #make sure the screen is in normal orientation when the script starts
    #keyboard interrupt handler
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
