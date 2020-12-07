FROM registry.in.linuxjedi.org/lnxjedi/gopherbot-theia:latest

USER root

ARG mdbookvers=v0.4.4
ARG hugovers=0.79.0
ARG kubectlvers=v1.18.12

RUN dnf -y install dnf-plugins-core && \
  dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo && \
  dnf -y reinstall shadow-utils && \
  dnf -y install \
    buildah \
    fuse-overlayfs \
    gh --exclude container-selinux && \
  dnf clean all && \
  rm -rf /var/cache /var/log/dnf* /var/log/dnf.*

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

RUN pip3 install awscli kubernetes ansible PyGithub && \
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

RUN chown -R ${USERID} ${HOME}

USER ${USERID}
