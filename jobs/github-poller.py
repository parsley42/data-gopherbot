#!/usr/bin/env python3

# github-poller.py - Loop through repositories.yaml and check github repos
# to see if they've changed. If so, start a gopherci build job.

import os
import sys
sys.path.append("%s/lib" % os.getenv("GOPHER_INSTALLDIR"))
from gopherbot_v2 import Robot
from github import Github

bot = Robot()
g = Github(os.getenv("GITHUB_TOKEN"))

repodata = bot.GetRepoData()

if not isinstance(repodata, dict):
    bot.Log("Warn", "github-poller triggered with invalid 'repositories.yaml', not a python 'dict'")
    exit(0)

# Pop off the executable path
sys.argv.pop(0)

# Retrive repo status memory
memory = bot.CheckoutDatum("repostats", True)
if not memory.exists:
    memory.datum = {}
repostats = memory.datum
print("Memory is: %s" % repostats)

def check_repo(org, name, repoconf):
    fullname = "%s/%s" % (org, name)
    if not fullname in repostats:
        repostats[fullname] = {}
    repostat = repostats[fullname]
    print("Checking repo %s" % fullname)
    repo = g.get_repo(fullname)
    for b in list(repo.get_branches()):
        name = b.name
        branch = repo.get_branch(name)
        commit = branch.commit.sha
        last = ""
        if name in repostat:
            last = repostat[name]
        repostat[name] = commit
        build = False
        if commit != last:
            build = True
        print("Found %s / %s: last built: %s, current: %s, build: %s" % (fullname, name, last, commit, build))
        if build:
            repotype = repoconf["Type"]
            bot.Log("Debug", "Adding primary build for github.com/%s (branch %s) to the pipeline, type '%s'" % (fullname, name, repotype))
            #bot.AddJob(repotype, [ "build", fullname, name ])

for reponame in repodata.keys():
    host, org, name = reponame.split("/")
    if host == "github.com":
        repoconf = repodata[reponame]
        repotype = repoconf["Type"]
        if len(repotype) != 0 and repotype != "none":
            check_repo(org, name, repoconf)

memory.datum = repostats
ret = bot.UpdateDatum(memory)
if ret != Robot.Ok:
    bot.Log("Error", "Unable to save long-term memory in github-poller: %s" % ret)
