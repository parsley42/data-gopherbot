#!/bin/bash

# data-dev.sh - run Data in a local dev container; start and connect to localhost:3000

podman run -it --name=data -p=127.0.0.1:3000:3000 --env-file=.env registry.in.linuxjedi.org/lnxjedi/gopherbot-k8s:latest
