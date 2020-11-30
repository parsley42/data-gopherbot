#!/bin/bash -e

# buildah-login.sh - buildah login for pushes

if [ $# -ne 3 ]
then
    echo "Missing arguments; usage: buildah-login <site> <user> <secretname>" >&2
    exit 1
fi

SITE=$1
USER=$2
SECRET=${3}

source $GOPHER_INSTALLDIR/lib/gopherbot_v1.sh

if [ ! "$REGISTRY_AUTH_FILE" ]
then
    export REGISTRY_AUTH_FILE=$(mktemp buildah-login.XXXXXX)
    echo '{}' > $REGISTRY_AUTH_FILE
    SetParameter REGISTRY_AUTH_FILE $REGISTRY_AUTH_FILE
    FinalTask exec rm -f $REGISTRY_AUTH_FILE
fi

cat <<<"${!SECRET}" | buildah login -u $USER --password-stdin $SITE
