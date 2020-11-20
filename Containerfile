FROM registry.in.linuxjedi.org/lnxjedi/gopherbot-theia:latest

USER root

ARG userid=1000
ARG homedir=/home/robot

ARG mdbookvers=v0.4.4
ARG kubectlvers=v1.18.12

RUN dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo && \
  dnf -y reinstall shadow-utils && \
  dnf -y install 'dnf-command(copr)' && \
  dnf -y copr enable rhcontainerbot/container-selinux && \
  curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable/CentOS_8_Stream/devel:kubic:libcontainers:stable.repo && \
  dnf -y install \
    buildah \
    fuse-overlayfs \
    gh && \
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

RUN pip3 install awscli kubernetes ansible && \
  curl -L -o /usr/local/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/${kubectlvers}/bin/linux/amd64/kubectl && \
  chmod +x /usr/local/bin/kubectl && \
  mkdir -p /sbin/.vscode-server && \
  chown 2:root /sbin/.vscode-server && \
  chmod u+rwx /sbin/.vscode-server

## Install mdbook
RUN cd /usr/local/bin && \
  curl -L https://github.com/rust-lang/mdBook/releases/download/${mdbookvers}/mdbook-${mdbookvers}-x86_64-unknown-linux-gnu.tar.gz | tar xzvf - && \
  chmod 755 mdbook

RUN chown -R robot:robot ${homedir}

USER ${userid}:${GROUP}
