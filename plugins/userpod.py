#!/usr/bin/python3

import os
import sys

executable = sys.argv.pop(0)
command = sys.argv.pop(0)

if command == "configure":
    exit(0)

import time
sys.path.append("%s/lib" % os.getenv("GOPHER_INSTALLDIR"))
from gopherbot_v2 import Robot
sys.path.append(os.getenv("GOPHER_CONFIGDIR"))
import podlib.userpod as userpod

bot = Robot()

if command == "init":
    exit(0)

if command == "types":
    pod_types = userpod.pod_types()
    say = [ "Pod types:" ]
    bot.Say("\n".join(say + pod_types))

if command == "launch":
    dom = os.getenv("USERPOD_DOM")
    ptype = sys.argv.pop(0)
    host = userpod.userpod(ptype, "parse", 1000, "project", 1000)
    while True:
        status = userpod.podstatus(host)
        if status == "Pending":
            time.sleep(2)
        else:
            if status == "Ready":
                bot.Say("Launched: https://%s.%s" % (host, dom))
            else:
                bot.Say("Failed: %s" % status)
            break