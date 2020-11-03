#!/usr/bin/python3

import os
import sys
import time
sys.path.append("%s/lib" % os.getenv("GOPHER_INSTALLDIR"))
from gopherbot_v2 import Robot
import podlib.pods as pods

bot = Robot()

executable = sys.argv.pop(0)
command = sys.argv.pop(0)

if command == "configure":
    exit(0)

if command == "init":
    exit(0)

if command == "types":
    pod_types = pods.podtypes()
    say = [ "Pod types:" ]
    bot.Say("\n".join(say + pod_types))

if command == "launch":
    dom = os.getenv("USERPOD_DOM")
    ptype = sys.argv.pop(0)
    host = pods.userpod(ptype, "parse", 1000, "project", 1000)
    while True:
        status = pods.podstatus(host)
        if status == "Pending":
            time.sleep(2)
        else:
            if status == "Ready":
                bot.Say("Launched: https://%s.%s" % (host, dom))
            else:
                bot.Say("Failed: %s" % status)
            break
