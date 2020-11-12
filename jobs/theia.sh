#!/bin/bash

# theia.sh - start theia interface; use ps & kill to terminate

SHELL=/bin/bash
THEIA_DEFAULT_PLUGINS=local-dir:/usr/local/theia/plugins
USE_LOCAL_GIT=true

export SHELL THEIA_DEFAULT_PLUGINS USE_LOCAL_GIT

cd /usr/local/theia
node /usr/local/theia/src-gen/backend/main.js /home/robot/custom --hostname 0.0.0.0
