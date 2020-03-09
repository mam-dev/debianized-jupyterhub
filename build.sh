#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# If you change this, you MUST also change "debian/control" and "debina/rules"
PYTHON_MINOR="3.8"  # Deadsnakes version on Ubuntu

# Check build environment
if ! command which "dh_listpackages" >/dev/null 2>&1; then
    echo >&2 "ERROR: You must 'apt install debhelper' on the build host."
    exit 1
fi

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name}"; shift
dist_id=${image%%:*}
codename=${image#*:}
pypi_name="$(./setup.py --name)"
pypi_version="$(./setup.py --version)"
pkgname="$(dh_listpackages)"
tag=$pypi_name-$dist_id-$codename
staging="$pypi_name-$pypi_version"

build_opts=(
    -f Dockerfile.build
    --tag $tag
    --build-arg "DIST_ID=$dist_id"
    --build-arg "CODENAME=$codename"
    --build-arg "PKGNAME=$pkgname"
)

if test "$dist_id" = "ubuntu"; then
    build_opts+=( --build-arg "PYVERSION=$PYTHON_MINOR" )
fi


# Create Docker staging directory and apply environment changes
echo "*** Creating staging directory (sdist)"
echo "*** Ignore warnings regarding non-matching filters..."
python3 ./setup.py -q sdist -k
if test "$dist_id" = "debian"; then
    sed -i -e "s/python$PYTHON_MINOR/python3/g" "$staging/debian/control"
fi

mkdir -p build
rm -rf build/docker.staging 2>/dev/null
mv "$staging" build/docker.staging


# Build in Docker container, save results, and show package info
echo
echo "*** Building DEB package (takes a while)"
rm -f dist/${pkgname}?*${pypi_version//./?}*${codename}*.*
docker build "${build_opts[@]}" "$@" build/docker.staging
mkdir -p dist
docker run --rm $tag tar -C /dpkg -c . | tar -C dist -x
ls -lh dist/${pkgname}?*${pypi_version//./?}*${codename}*.*
