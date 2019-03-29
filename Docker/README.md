# Python3 Kernel Docker Image

The Dockerfile in this directory comes with the exact same software
stack as the Debian package.

Build the image by calling…

```sh
pyenv_version=1.2.9
gitroot="$(git rev-parse --show-toplevel)"
version=$(command cd "$gitroot" >/dev/null && ./setup.py --version)
test -f "$gitroot/requirements.txt" || touch "$gitroot/requirements.txt"
( cd "$gitroot/Docker" &&
  ( test -f v${pyenv_version}.tar.gz \
    || wget https://github.com/pyenv/pyenv/archive/v${pyenv_version}.tar.gz ) &&
  docker build --tag ono-py3-kernel:latest \
               --tag ono-py3-kernel:$version \
               --build-arg pyenv_version=${pyenv_version} \
               -f "$gitroot/Docker/Dockerfile" \
               "$gitroot" )
```

This integrates the Python version as determined by the `pyversion` Docker `ARG`,
using [pyenv](https://github.com/pyenv/pyenv).

To start a notebook server using this image, call this comamnd:

```sh
docker run --rm -it --network host ono-py3-kernel
```

To kill the running notebook from the outside:

```sh
docker kill $(docker ps | grep ono-py3-kernel | cut -f1 -d' ')
```

And to experiment with the image, e.g. installing new packages to try them out
(`distro` in the example), run it with `bash` as the entry point.

```sh
docker run --rm -it --network host --entrypoint /bin/bash --user root ono-py3-kernel
pip install distro
su -s /bin/sh -c 'jupyter notebook --ip=127.0.0.1 --port=8900' jupyter
```

You can only install pure Python packages or pre-built wheels,
since build tooling is not available.
