#!/bin/bash

docker pull quay.io/lnxjedi/gopherbot-theia:latest
docker build -f Containerfile -t registry.in.linuxjedi.org/lnxjedi/gopherbot-k8s:latest .
