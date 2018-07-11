# "jupyterhub" Debian Packaging

**STATUS** :construction: Package building works, and you can launch the server
using ``/usr/sbin/jupyterhub-launcher`` in a ``root`` console window. It'll use PAM authorization,
i.e. starts the notebook servers in a local user's context. Tested on *Ubuntu Xenial* so far.


![BSD 3-clause licensed](https://img.shields.io/badge/license-BSD_3--clause-red.svg)
[![debianized-jupyterhub](https://img.shields.io/pypi/v/debianized-jupyterhub.svg)](https://pypi.python.org/pypi/debianized-jupyterhub/)
[![jupyterhub](https://img.shields.io/pypi/v/jupyterhub.svg)](https://pypi.python.org/pypi/jupyterhub/)

**Contents**

 * [What is this?](#what-is-this)
 * [How to build and install the package](#how-to-build-and-install-the-package)
 * [Trouble-Shooting](#trouble-shooting)
   * ['npm' errors while building the package](#npm-errors-while-building-the-package)
   * ['pkg-resources not found' or similar during virtualenv creation](#pkg-resources-not-found-or-similar-during-virtualenv-creation)
   * ['no such option: --no-binary' during package builds](#no-such-option---no-binary-during-package-builds)
 * [How to set up a simple service instance](#how-to-set-up-a-simple-service-instance)
 * [Changing the Service Unit Configuration](#changing-the-service-unit-configuration)
 * [Configuration Files](#configuration-files)
 * [Data Directories](#data-directories)
 * [TODOs](#todos)
 * [References](#references)
   * [Documentation Links](#documentation-links)
   * [Related Projects](#related-projects)
   * [Things to Look At](#things-to-look-at)


## What is this?

This project provides packaging of the core *JupyterHub* components, so they can be easily installed on Debian-like target hosts .
This makes life-cycle management on production hosts a lot easier, and
[avoids common drawbacks](https://nylas.com/blog/packaging-deploying-python/) of ‘from source’ installs,
like needing build tools and direct internet access in production environments.

The Debian packaging metadata in
[debian](https://github.com/1and1/debianized-jupyterhub/tree/master/debian)
puts the `jupyterhub` Python package and its dependencies as released on PyPI into a DEB package,
using [dh-virtualenv](https://github.com/spotify/dh-virtualenv).
The resulting *omnibus package* is thus easily installed to and removed from a machine,
but is not a ‘normal’ Debian `python-*` package. If you want that, look elsewhere.

Since the dynamic router of *JupyterHub* is a *Node.js* application, the package also has a dependency on `nodejs`,
limited to the current LTS version range (that is 8.x as of this writing).
In practice, that means you should use the
[NodeSource](https://github.com/nodesource/distributions#nodesource-nodejs-binary-distributions)
packages to get *Node.js*,
since the native *Debian* ones are typically dated (*Stretch* comes with  ``4.8.2~dfsg-1``).
Adapt the ``debian/control`` file if your requirements are different.

To add any plugins or other optional *Python* dependencies, list them in ``install_requires`` in ``setup.py`` as usual
– but only use versioned dependencies so package builds are reproducible.
``seaborn`` is added by default, which in turn pulls large parts of the usual data science stack, including
``numpy``, ``scipy``, ``pandas``, and ``matplotlib``.


## How to build and install the package

You need a build machine with all build dependencies installed, specifically
[dh-virtualenv](https://github.com/spotify/dh-virtualenv) in addition to the normal Debian packaging tools.
You can get it from [this PPA](https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv),
the [official Ubuntu repositories](http://packages.ubuntu.com/search?keywords=dh-virtualenv),
or [Debian packages](https://packages.debian.org/source/sid/dh-virtualenv).

This code requires and is tested with ``dh-virtualenv`` v1.0
– depending on your platform you might get an older version via the standard packages.
*Zesty* provides a package for *Ubuntu* that works on older releases too,
see *“Extra steps on Ubuntu”* below for how to use it.
In all other cases build *v1.0* from source,
see the [dh-virtualenv documentation](https://dh-virtualenv.readthedocs.io/en/latest/tutorial.html#step-1-install-dh-virtualenv) for that.

With tooling installed,
the following commands will install a *release* version of `jupyterhub` into `/opt/venvs/jupyterhub/`,
and place a symlink for the `jupyterhub` command into the machine's PATH.

```sh
git clone https://github.com/1and1/debianized-jupyterhub.git
cd debianized-jupyterhub/
# or "pip download --no-deps --no-binary :all: debianized-jupyterhub" and unpack the archive

sudo apt-get install build-essential debhelper devscripts equivs

# Extra steps on Ubuntu
( cd /tmp && curl -LO "http://mirrors.kernel.org/ubuntu/pool/universe/d/dh-virtualenv/dh-virtualenv_1.0-1_all.deb" )
sudo dpkg -i /tmp/dh-virtualenv_1.0-1_all.deb
# END Ubuntu

sudo mk-build-deps --install debian/control
dpkg-buildpackage -uc -us -b
dpkg-deb -I ../jupyterhub_*.deb
```

The resulting package, if all went well, can be found in the parent of your project directory.
You can upload it to a Debian package repository via e.g. `dput`, see
[here](https://github.com/jhermann/artifactory-debian#package-uploading)
for a hassle-free solution that works with *Artifactory* and *Bintray*.

You can also install it directly on the build machine:

```sh
sudo dpkg -i ../jupyterhub_*.deb
/usr/sbin/jupyterhub --version  # ensure it basically works
```

To list the installed version of `jupyterhub` and all its dependencies, call this:

```sh
/opt/venvs/jupyterhub/bin/pip freeze | column
```


## Trouble-Shooting

### 'npm' errors while building the package

While installing the ``configurable-http-proxy`` Javascript module,
you might get errors like ``npm ERR! code E403``.
That specific error means you have to provide authorization with your *Node.js* registry.

``npm`` uses a configuration file which can provide both
a local registry URL and the credentials for it.
Create a ``.npmrc`` file in the root of your git working directory,
otherwise ``~/.npmrc`` is used.

**Example ‘.npmrc’ file:**

```ini
_auth = xyzb64…E=
always-auth = true
email = joe.schmoe@example.com
```


### 'pkg-resources not found' or similar during virtualenv creation

If you get errors regarding ``pkg-resources`` during the virtualenv creation,
update your build machine's ``pip`` and ``virtualenv``.
The versions on many distros are just too old to handle current infrastructure (especially PyPI).

This is the one exception to “never sudo pip”, so go ahead and do this:

```sh
sudo pip install -U pip virtualenv
```

Then try building the package again.


### 'no such option: --no-binary' during package builds

This package needs a reasonably recent `pip` for building.
On `Debian Jessie`, for the internal `pip` upgrade to work,
that means you need a newer `pip` on the system,
or else at least `dh-virtualenv 1.1` installed (as of this writing, that is *git HEAD*).

To upgrade `pip` (which makes sense anyway, version 1.5.6 is ancient), call ``sudo pip install -U pip``.

And to get `dh-virtualenv 1.1` right now on `Jessie`, you need to apply this patch *before* building it:

```diff
--- a/debian/changelog
+++ b/debian/changelog
@@ -1,3 +1,9 @@
+dh-virtualenv (1.1-1~~dev1) unstable; urgency=medium
+
+  * Non-maintainer upload.
+
+ -- Juergen Hermann <jh@web.de>  Wed, 20 Jun 2018 10:22:32 +0000
+
 dh-virtualenv (1.0-1) unstable; urgency=medium

   * New upstream release
--- a/debian/rules
+++ b/debian/rules
@@ -1,7 +1,7 @@
 #!/usr/bin/make -f

 %:
-       dh $@ --with python2 --with sphinxdoc
+       dh $@ --with python2

 override_dh_auto_clean:
        rm -rf doc/_build
@@ -13,6 +13,3 @@ override_dh_auto_build:
        rst2man doc/dh_virtualenv.1.rst > doc/dh_virtualenv.1
        dh_auto_build

-override_dh_installdocs:
-       python setup.py build_sphinx
-       dh_installdocs doc/_build/html

--- a/setup.py
+++ b/setup.py
@@ -25,7 +25,7 @@ from setuptools import setup

 project = dict(
     name='dh_virtualenv',
-    version='1.0',
+    version='1.1.dev1',
     author=u'Jyrki Pulliainen',
     author_email='jyrki@spotify.com',
     url='https://github.com/spotify/dh-virtualenv',
```

See [this ticket](https://github.com/spotify/dh-virtualenv/issues/234) for details,
and hopefully for a resolution at the time you read this.


## How to set up a simple service instance

**TODO** Link to packaged project's documentation, and adapt the text below as needed!

After installing the package, …

The package contains a ``systemd`` unit for the service, and starting it is done via ``systemctl``:

```sh
sudo systemctl enable jupyterhub
sudo systemctl start jupyterhub

# This should show the service in state "active (running)"
systemctl status 'jupyterhub' | grep -B2 Active:
```

The service runs as ``jupyterhub.daemon``.
Note that the ``jupyterhub`` user is not removed when purging the package,
but the ``/var/{log,opt}/jupyterhub`` directories and the configuration are.

**TODO** After an upgrade, the services restart automatically by default,


## Changing the Service Unit Configuration

The best way to change or augment the configuration of a *systemd* service
is to use a ‘drop-in’ file.
For example, to increase the limit for open file handles
above the system defaults, use this in a **``root``** shell:

```sh
unit='jupyterhub'

# Change max. number of open files for ‘$unit’…
mkdir -p /etc/systemd/system/$unit.service.d
cat >/etc/systemd/system/$unit.service.d/limits.conf <<'EOF'
[Service]
LimitNOFILE=8192
EOF

systemctl daemon-reload
systemctl restart $unit

# Check that the changes are effective…
systemctl cat $unit
let $(systemctl show $unit -p MainPID)
cat "/proc/$MainPID/limits" | egrep 'Limit|files'
```


## Configuration Files

 * ``/etc/default/jupyterhub`` – Operational parameters like log levels and port bindings.
 * ``/etc/jupyterhub/jupyterhub_config.py`` – The service's configuration.

 :information_source: Please note that the files in ``/etc/jupyterhub``
 are *not* world-readable, since they might contain passwords.


## Data Directories

 * ``/var/log/jupyterhub`` – Extra log files.
 * ``/var/opt/jupyterhub`` – Data files created during runtime (``jupyterhub_cookie_secret``, ``jupyterhub.sqlite``, …).

You should stick to these locations, because the maintainer scripts have special handling for them.
If you need to relocate, consider using symbolic links to point to the physical location.


## TODOs

 * Use ``/srv/jupyterhub`` as the data dir?
 * [Put user notebook dirs into the data dir](https://jupyterhub.readthedocs.io/en/stable/getting-started/spawners-basics.html)
 * Add a global ``jupyter_notebook_config.py``
 * https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html
 * https://jupyterhub.readthedocs.io/en/stable/reference/config-sudo.html
 * [cull_idle_servers](https://jupyterhub.readthedocs.io/en/stable/getting-started/services-basics.html)
 * Prometheus monitoring
 * Run the proxy as a separate systemd service?
 * Replace CHP by Træfik, an F5 integration, or similar


## References

### Documentation Links

These links point to parts of the documentation especially useful for operating a JupyterHub installation.

 * [Troubleshooting](https://jupyterhub.readthedocs.io/en/stable/troubleshooting.html#troubleshooting)

   * [Troubleshooting Commands](https://jupyterhub.readthedocs.io/en/stable/troubleshooting.html#troubleshooting-commands)


### Related Projects

 * [Springerle/debianized-pypi-mold](https://github.com/Springerle/debianized-pypi-mold) – Cookiecutter that was used to create this project.

### Things to Look At

 * [jupyter/docker-stacks](https://github.com/jupyter/docker-stacks) – Ready-to-run Docker images containing Jupyter applications.
 * [jupyter/repo2docker](https://github.com/jupyter/repo2docker) – Turn git repositories into Jupyter-enabled Docker Images.
 * [vatlab/SoS](https://github.com/vatlab/SOS) – Workflow system designed for daily data analysis.
