FROM quay.io/lnxjedi/gopherbot-theia:latest

USER root

ARG mdbookvers=v0.4.7
ARG hugovers=0.81.0
ARG kubectlvers=v1.20.4

RUN . /etc/os-release && \
  echo "deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/x${NAME}_${VERSION_ID}/ /" > /etc/apt/sources.list.d/kubic.list && \
  curl -L https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/x${NAME}_${VERSION_ID}/Release.key  | apt-key add - && \
  echo "deb https://cli.github.com/packages ${UBUNTU_CODENAME} main" > /etc/apt/sources.list.d/github.list && \
  apt-key adv --keyserver keyserver.ubuntu.com --recv-key C99B11DEB97541F0 && \
  apt-get update && \
  apt-get install -y \
    buildah \
    fuse-overlayfs \
    gh && \
  rm -rf /var/lib/apt/lists/*

# Set an environment variable to default to chroot isolation for RUN
# instructions and "buildah run".
ENV BUILDAH_ISOLATION=chroot

COPY containers.conf /etc/containers/containers.conf

# Adjust storage.conf to enable Fuse storage.
RUN chmod 644 /etc/containers/containers.conf && \
  sed -i \
    -e 's|^#mount_program|mount_program|g' \
    -e '/additionalimage.*/a "/var/lib/shared",' \
    -e 's|^mountopt[[:space:]]*=.*$|mountopt = "nodev,fsync=0"|g' \
    /etc/containers/storage.conf && \
  mkdir -p \
    /var/lib/shared/overlay-images \
    /var/lib/shared/overlay-layers \
    /var/lib/shared/vfs-images \
    /var/lib/shared/vfs-layers && \
  touch \
    /var/lib/shared/overlay-images/images.lock \
    /var/lib/shared/overlay-layers/layers.lock \
    /var/lib/shared/vfs-images/images.lock \
    /var/lib/shared/vfs-layers/layers.lock

RUN pip3 install \
    ansible \
    awscli \
    kubernetes && \
  rm -rf ${HOME}/.cache && \
  curl -L -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${kubectlvers}/bin/linux/amd64/kubectl && \
  chmod +x /usr/local/bin/kubectl && \
  mkdir -p /sbin/.vscode-server && \
  chown 2:root /sbin/.vscode-server && \
  chmod u+rwx /sbin/.vscode-server

## Install mdbook & hugo
RUN cd /usr/local/bin && \
  curl -L https://github.com/rust-lang/mdBook/releases/download/${mdbookvers}/mdbook-${mdbookvers}-x86_64-unknown-linux-gnu.tar.gz | tar xzvf - && \
  curl -L https://github.com/gohugoio/hugo/releases/download/v${hugovers}/hugo_${hugovers}_Linux-64bit.tar.gz | tar xzvf - hugo && \
  chmod 755 mdbook hugo

USER 1000
