#!/bin/bash

# theia.sh - start theia interface; use ps & kill to terminate

source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh

umask 0002

SHELL=/bin/bash
THEIA_DEFAULT_PLUGINS=local-dir:/usr/local/theia/plugins
USE_LOCAL_GIT=true

export SHELL THEIA_DEFAULT_PLUGINS USE_LOCAL_GIT

cat > $HOME/.bashrc <<EOF
# File created by jobs/theia.sh
PS1="\[\033[01;32m\]robot@gopherbot-dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
PATH=$HOME/bin:$HOME/.local/bin:$HOME/go/bin:/opt/gopherbot:$PATH
export PATH PS1
EOF

cd /usr/local/theia
exec node /usr/local/theia/src-gen/backend/main.js /home/robot --hostname 0.0.0.0
