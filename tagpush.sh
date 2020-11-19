#!/bin/bash

# tagpush.sh - push container builds to home cluster registry

for CONTAINER in gopherbot gopherbot-dev gopherbot-theia
do
    buildah tag quay.io/lnxjedi/$CONTAINER:latest registry.in.linuxjedi.org/lnxjedi/$CONTAINER:latest
    buildah push registry.in.linuxjedi.org/lnxjedi/$CONTAINER:latest
done