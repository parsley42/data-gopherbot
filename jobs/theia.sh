#!/bin/bash

# theia.sh - start theia interface; use ps & kill to terminate

source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh

FailTask tail-log

cat > $HOME/.bashrc <<EOF
# File created by jobs/theia.sh
PS1="\[\033[01;32m\]robot@gopherbot-dev\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
PATH=$HOME/bin:$HOME/.local/bin:$HOME/go/bin:/opt/gopherbot:$PATH
export PATH PS1
EOF

cat > $HOME/stop-theia.sh <<"EOF"
kill $PPID
EOF

ln -snf /opt/gopherbot $HOME/robot-defaults || Say "Failed to create symlink $HOME/robot-defaults"

AddTask git-init $GOPHER_CUSTOM_REPOSITORY
AddTask run-theia
