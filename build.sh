#!/bin/bash

podman pull quay.io/lnxjedi/gopherbot-theia:latest
podman build -f Containerfile -t registry.in.linuxjedi.org/lnxjedi/gopherbot-k8s:latest .
