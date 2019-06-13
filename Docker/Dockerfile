# Python 3.7 Kernel on Bionic (based on pyenv)
# ============================================
#
# See README.md for instructions.
#
# 'python-build' docs:
#   https://github.com/pyenv/pyenv/tree/master/plugins/python-build
#

ARG extras=default
ARG distro=ubuntu:bionic
ARG pyversion=3.7.2
ARG pyenv_version=1.2.9
ARG pyenv_url=https://github.com/pyenv/pyenv/archive/v${pyenv_version}.tar.gz

FROM ${distro} AS builder
ARG extras

# Install build dependencies for 'python-build'
RUN env LANG=C apt-get update -qq -o Acquire::Languages=none \
    && env LANG=C DEBIAN_FRONTEND=noninteractive apt-get install \
        -y --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        \
        build-essential \
        ca-certificates \
        curl \
        dpkg-dev \
        libparse-debianchangelog-perl \
        llvm \
        make \
        wget \
        xz-utils \
        \
        libbz2-dev \
        libdb-dev \
        libexpat1-dev \
        libffi-dev \
        libfreetype6-dev \
        libgdbm-dev \
        libcurl4-openssl-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libtar-dev \
        libtinfo-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libz-dev \
        libzip-dev \
        tk-dev \
        zlib1g-dev \
        \
        less \
        vim \
    && apt-get clean && rm -rf "/var/lib/apt/lists"/*

# Build selected Python version using 'pyenv'
ARG pyversion
ARG pyenv_version
WORKDIR /opt
COPY Docker/v${pyenv_version}.tar.gz ./
RUN tar --strip-components=1 -xzf v${pyenv_version}.tar.gz \
    && export PYENV_ROOT=$PWD \
    && ( cd plugins/python-build && ./install.sh ) \
    && mkdir -p python \
    && { python-build -v ${pyversion} $PWD/python; RC=$?; } \
    && tail -n33 $(ls -1rt /tmp/*.log | tail -n1) \
    && echo RC=$RC

# Update Python tools
RUN /opt/python/bin/python3 -m pip install --no-warn-script-location -U pip \
    && /opt/python/bin/python3 -m pip install --no-warn-script-location -U setuptools wheel

# Build source-only native wheels
COPY setup.py MANIFEST.in /tmp/
COPY debian/changelog debian/control debian/rules /tmp/debian/
RUN mkdir -p /opt/python/wheels \
    && /opt/python/bin/python3 -m pip install --no-warn-script-location \
                               $(egrep Cython /tmp/setup.py | cut -f2 -d"'") \
    && /opt/python/bin/python3 -m pip wheel -w /opt/python/wheels \
                               psutil \
                               $(egrep pycurl /tmp/setup.py | cut -f2 -d"'") \
                               $(egrep word2vec /tmp/setup.py | cut -f2 -d"'") \
                               $(egrep Pillow /tmp/setup.py | cut -f2 -d"'") \
                               -e /tmp/.[$extras]

# Reduce size of runtime image by removing cruft (lib: 188M → 55M)
RUN cd python && rm -rf \
        lib/libpython*.a \
        lib/python*/config-*-*-linux-gnu \
        lib/python*/ensurepip \
        lib/python*/idlelib \
        lib/python*/lib2to3 \
        \
        lib/python*/test \
        \
        lib/python*/turtle.py \
        lib/python*/turtledemo \
        lib/python*/__pycache__/turtle.*.pyc \
        lib/python*/__pycache__/*.opt-?.pyc

# Report library dependencies and top-level dir sizes
RUN find /opt/python/ -name *.so | xargs ldd \
    | egrep -v '^/opt/py|libc.so|libm.so' | awk '{print $1}' | sort -u \
    | xargs dpkg -S | cut -f1 -d: | sort -u \
    && du -sch /opt/python/*


# Build runtime image
FROM ${distro} AS runtime
LABEL maintainer="Juergen Hermann <jh@web.de>"
# http://label-schema.org/
LABEL org.label-schema.schema-version="0.9.5.1"
LABEL org.label-schema.name="ono-py3-kernel"
LABEL org.label-schema.description="Python3 JupyterHub Kernel"
LABEL org.label-schema.url="https://github.com/1and1/debianized-jupyterhub/blob/master/Docker"
LABEL org.label-schema.vcs-url="https://github.com/1and1/debianized-jupyterhub.git"
ARG extras

ENV LANG=en_US.UTF-8
RUN env LANG=C apt-get update -qq -o Acquire::Languages=none \
    && env LANG=C DEBIAN_FRONTEND=noninteractive apt-get install \
        -yqq --no-install-recommends -o Dpkg::Options::=--force-unsafe-io \
        \
        ca-certificates \
        locales \
        mime-support \
        libparse-debianchangelog-perl \
        \
        libbsd0 \
        libbz2-1.0 \
        libcurl4 \
        libdb5.3 \
        libexpat1 \
        libffi6 \
        libfreetype6 \
        $(apt-cache search libgdbm[0-9] | awk '{print $1}') \
        libncursesw5 \
        libpng16-16 \
        libreadline7 \
        libsqlite3-0 \
        libssl1.1 \
        libtinfo5 \
        zlib1g \
        \
        libtcl8.6 \
        libtk8.6 \
        tix \
        tk8.6-blt2.5 \
    && echo "$LANG UTF-8" >/etc/locale.gen \
    && locale-gen --lang "$LANG" \
    && apt-get clean && rm -rf "/var/lib/apt/lists"/*
COPY --from=builder /opt/python /opt/python
COPY debian/rules /tmp
COPY requirements.txt /tmp
RUN groupadd jupyter \
    && useradd -g jupyter -G jupyter,users -c "Jupyter User" -s /bin/bash --create-home jupyter \
    && chmod 750 ~jupyter \
    && chown -R jupyter.jupyter ~jupyter \
    && ( echo 'jupyter:demo' | chpasswd ) \
    && /opt/python/bin/python3 -m pip install -f /opt/python/wheels \
                               --no-warn-script-location \
                               debianized-jupyterhub[$extras] \
    && /opt/python/bin/python3 -m pip install -r /tmp/requirements.txt \
    && /opt/python/bin/python3 -m pip uninstall -y debianized-jupyterhub \
    && bash -c "rm -rf /opt/python/lib/python3.*/site-packages/phantomjs_bin/bin/{macosx,windows}" \
    && ln -s /opt/python/bin/* /usr/local/bin
WORKDIR /home/jupyter
USER jupyter
COPY --chown=jupyter:jupyter docs/examples/*.ipynb ./
EXPOSE 8900 8901
CMD jupyter notebook --ip=127.0.0.1 --port=8900
