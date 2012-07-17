# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Peter Levi <peterlevi@peterlevi.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import optparse

import gettext
from gettext import gettext as _
gettext.textdomain('variety')

from gi.repository import Gtk, Gdk, GObject # pylint: disable=E0611

from variety import VarietyWindow

from variety_lib import set_up_logging, get_version

import os
import sys
import signal

def parse_options():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs variety_lib also)"))
    (options, args) = parser.parse_args()

    set_up_logging(options)

VARIETY_WINDOW = None

def sigint_handler(a, b):
    print "CTRL-C pressed, quitting..."
    global VARIETY_WINDOW
    if VARIETY_WINDOW:
        VARIETY_WINDOW.on_quit()
    sys.exit()

def main():
    'constructor for your class instances'

    # ignore Ctrl-C
    signal.signal(signal.SIGINT, sigint_handler)

    parse_options()

    # ensure singleton
    check_pid()

    # Run the application.
    window = VarietyWindow.VarietyWindow()
    global VARIETY_WINDOW
    VARIETY_WINDOW = window
    window.first_run()

    GObject.threads_init()
    Gdk.threads_init()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()

def check_pid():
    try:
        os.makedirs(os.path.expanduser("~/.config/variety"))
    except Exception:
        pass

    lock = os.path.expanduser("~/.config/variety/.lock")

    if os.access(lock, os.F_OK):
        try:
            # If the lockfile is already there then check the PID number in the lock file
            with open(lock, "r") as pidfile:
                pidfile.seek(0)
                old_pd = str(int(pidfile.readline().strip()))

                try:
                    # Now we check if the PID from lock file matches to the current process PID
                    if os.path.exists("/proc/%s" % old_pd):
                        with open("/proc/%s/cmdline" % old_pd) as f:
                            if f.read().find("variety") >= 0:
                                print "You already have an instance of the program running, process ID %s. Exiting." % old_pd
                                sys.exit(1)
                except Exception:
                    pass

                print "Lock file is there but the program is not running."
                print "Removing lock file as it can be there because the program crashed last time it was run as process ID %s." % old_pd
                os.remove(lock)

        except Exception:
            print "Lock file is there but is unreadable or contains garbage."
            print "Removing bad lock file and running the program."
            os.remove(lock)

    # Put a PID in the lock file
    pidfile = open(lock, "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close()
