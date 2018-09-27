#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name}"; shift
dist_id=${image%%:*}
codename=${image#*:}
pypi_name="$(./setup.py --name)"
pkgname="$(dh_listpackages)"
pkgversion="$(dpkg-parsechangelog -S Version)"
tag=$pypi_name-$dist_id-$codename
staging_dir="build/staging"

# Prepare staging area
rm -rf $staging_dir 2>/dev/null || true
mkdir -p $staging_dir
git ls-files >build/git-files
rm -f build/${pkgname}?*${pkgversion}*.*
test ! -f .npmrc || echo .npmrc >>build/git-files
tar -c --files-from build/git-files | tar -C $staging_dir -x

# Build in Docker container, save results, and show package info
docker build --tag $tag \
    --build-arg "DIST_ID=$dist_id" \
    --build-arg "CODENAME=$codename" \
    --build-arg "PKGNAME=$pkgname" \
    -f Dockerfile.build \
    "$@" $staging_dir
docker run --rm $tag tar -C /dpkg -c . | tar -C build -xv
