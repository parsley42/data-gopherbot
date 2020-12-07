#!/bin/bash -e

# quaytrigger.sh - trigger a container build on quay.io
# NOTE: this is NOT general-purpose, but hard-coded to use
# with github.com/lnxjedi/gopherbot-base-contaienrs

trap_handler()
{
    ERRLINE="$1"
    ERRVAL="$2"
    echo "line ${ERRLINE} exit status: ${ERRVAL}" >&2
    # The script should usually exit on error
    exit $ERRVAL
}
trap 'trap_handler ${LINENO} $?' ERR

source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh
AddTask email-log parsley@linuxjedi.org

REPO=$1
WEBHOOK_ENV=$(echo $REPO | tr - _)
WEBHOOK=${!WEBHOOK_ENV}

COMMIT=$(gh api /repos/lnxjedi/gopherbot-base-containers/branches | jq -r '.[] | select(.name=="master") | .commit.sha')

echo "{ \"commit\": \"$COMMIT\", \"ref\": \"refs/heads/master\", \"default_branch\": \"master\" }" | curl -X POST -H "Content-Type: application/json" -d @- $WEBHOOK
