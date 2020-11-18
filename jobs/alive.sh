#!/bin/bash -e

# jobs/alive.sh - send a weekly "I'm alive" email to keep Gmail from disabling email

# NOTE: this sample job uses the bot library, most jobs probably won't
source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh

echo "I'm alive - $(date)"

AddTask email-log parsley@linuxjedi.org
