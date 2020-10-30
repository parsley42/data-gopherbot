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

if command == "launch":
    dom = "dev.uvarc.io"
    host = pods.userpod("theia-python", "dlp7y@virginia.edu", 2000, "askljsdfoobar", 2000)
    isbot = os.getenv("GOPHER_INSTALLDIR") != None
    while True:
        status = pods.podstatus(host)
        if status == "Pending":
            if not isbot:
                print("Pending")
            time.sleep(2)
        else:
            if status == "Ready":
                if isbot:
                    bot.Say("Launched: https://%s.%s" % (host, dom))
                else:
                    print("Launched: https://%s.%s" % (host, dom))
            else:
                if isbot:
                    bot.Say("Failed: %s" % status)
                else:
                    print("Failed: %s" % status)
            break
