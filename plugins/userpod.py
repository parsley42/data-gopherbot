#!/usr/bin/python3

import os
import sys
import time
sys.path.append("%s/lib" % os.getenv("GOPHER_INSTALLDIR"))
from gopherbot_v2 import Robot
cfgdir = os.getenv("GOPHER_CONFIGDIR")
sys.path.append(cfgdir)
import podlib.userpod as userpod

bot = Robot()

executable = sys.argv.pop(0)
command = sys.argv.pop(0)

if command == "configure":
    exit(0)

if command == "init":
    exit(0)

if command == "types":
    pod_types = userpod.pod_types()
    say = [ "Pod types:" ]
    bot.Say("\n".join(say + pod_types))

if command == "list":
    pod_dns = userpod.userpods("parse")
    say = [ "Running pods:" ]
    bot.Say("\n".join(say + pod_dns))

if command == "launch":
    ptype = sys.argv.pop(0)
    annotations = {
        "nginx.ingress.kubernetes.io/auth-tls-secret": "admin/linuxjedi-ca-cert",
        "nginx.ingress.kubernetes.io/auth-tls-verify-client": "on",
    }
    host = userpod.userpod(ptype, "parse", "parsley@linuxjedi.org", 1000, 1000, "project", 1001, annotations)
    while True:
        status = userpod.podstatus(host)
        if status == "Pending":
            time.sleep(2)
        else:
            if status == "Ready":
                bot.Say("Launched: https://%s" % host)
            else:
                bot.Say("Failed: %s" % status)
            break

if command == "terminate":
    pod = sys.argv.pop(0)
    userpod.terminate(pod)
    bot.Say("Terminated.")
