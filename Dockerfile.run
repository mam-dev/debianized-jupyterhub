# Install and run JupyterHub on Debian Stretch
# ============================================
#
#   ./build.sh debian:stretch
#   docker build --tag jupyterhub-stretch:latest --tag jupyterhub-stretch:$(./setup.py --version) -f Dockerfile.run dist
#   docker run --rm -it -p 8000:8000 -p 8001:8001 --name jupyterhub-stretch jupyterhub-stretch
#
# To copy examples and open Jupyter (do this in another terminal):
#
#   ( builtin cd docs/examples/ >/dev/null && tar -c *.ipynb ) | docker exec -i $(docker ps | grep jupyterhub-stretch | cut -f1 -d' ') bash -c "cd /home/admin && tar -xv"
#   xdg-open "http://127.0.0.1:8000/user/admin/tree"
#
# The password for the `admin` account is `test1234`.
#
# To enter the container:
#
#   docker exec -it $(docker ps | grep jupyterhub-stretch | cut -f1 -d' ') bash
#

FROM debian:stretch
ENV LANG=en_US.UTF-8
RUN env LANG=C apt-get update -qq -o Acquire::Languages=none \
    && env LANG=C DEBIAN_FRONTEND=noninteractive apt-get install \
        -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        apt-transport-https \
        apt-utils \
        ca-certificates \
        curl \
        gnupg2 \
        less \
        libyaml-0-2 \
        libz1 \
        locales \
        perl \
        python3-tk \
        sudo \
        vim \
    && echo "$LANG UTF-8" >/etc/locale.gen \
    && locale-gen --lang "$LANG" \
    && echo 'deb https://deb.nodesource.com/node_10.x stretch main' \
            >/etc/apt/sources.list.d/nodesource.list \
    && ( curl -sL https://deb.nodesource.com/gpgkey/nodesource.gpg.key \
         | env APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=true apt-key add - ) \
    && env LANG=C apt-get update -qq -o Acquire::Languages=none \
    && env LANG=C DEBIAN_FRONTEND=noninteractive apt-get install \
        -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        nodejs \
    && apt-get clean && rm -rf "/var/lib/apt/lists"/*
WORKDIR /srv/jupyterhub
COPY jupyterhub_[0-9]*~stretch_amd64.deb ./
RUN echo JUPYTERHUB_AUTO_RESTART=false >/etc/default/jupyterhub \
    && dpkg -i --force-confold --force-unsafe-io jupyterhub_[0-9]*~stretch_amd64.deb \
    && groupadd jhub \
    && useradd -g jhub -G jhub,users -c "JupyterHub Admin" -s /bin/bash --create-home admin \
    && chmod 750 ~admin \
    && chown -R admin.jhub ~admin \
    && ( echo 'admin:test1234' | chpasswd )
EXPOSE 8000 8001
ENTRYPOINT su -s /bin/sh -c /usr/sbin/jupyterhub-launcher jupyterhub
