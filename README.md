# "jupyterhub" Debian Packaging

**STATUS** :ballot_box_with_check: Package building works, and you can launch the server
using ``systemctl start jupyterhub``, or via the provided ``Dockerfile.run``.
It'll use PAM authorization, i.e. starts the notebook servers in a local user's context.
The package is tested on *Ubuntu Bionic*, on *Ubuntu Xenial* (with Python 3.6 from the *Deadsnakes PPA*),
and on *Debian Stretch*. You can also use a Docker container
(see ``Dockerfile.run`` / user: ``admin`` / pwd: ``test1234``).


![BSD 3-clause licensed](https://img.shields.io/badge/license-BSD_3--clause-red.svg)
[![debianized-jupyterhub](https://img.shields.io/pypi/v/debianized-jupyterhub.svg)](https://pypi.python.org/pypi/debianized-jupyterhub/)
[![jupyterhub](https://img.shields.io/pypi/v/jupyterhub.svg)](https://pypi.python.org/pypi/jupyterhub/)

**Contents**

 * [What is this?](#what-is-this)
 * [“Devops Intelligence” showcase](#devops-intelligence-showcase)
 * [How to build and install the package](#how-to-build-and-install-the-package)
   * [Building in a Docker container](#building-in-a-docker-container)
   * [Building directly on your workstation](#building-directly-on-your-workstation)
 * [Trouble-Shooting](#trouble-shooting)
   * ['npm' errors while building the package](#npm-errors-while-building-the-package)
   * ['pkg-resources not found' or similar during virtualenv creation](#pkg-resources-not-found-or-similar-during-virtualenv-creation)
   * ['no such option: --no-binary' during package builds](#no-such-option---no-binary-during-package-builds)
 * [Updating requirements](#updating-requirements)
 * [How to set up a simple service instance](#how-to-set-up-a-simple-service-instance)
 * [Securing your JupyterHub web service with an SSL off-loader](#securing-your-jupyterhub-web-service-with-an-ssl-off-loader)
 * [Changing the Service Unit Configuration](#changing-the-service-unit-configuration)
 * [Configuration Files](#configuration-files)
 * [Data Directories](#data-directories)
 * [References](#references)
   * [Documentation Links](#documentation-links)
   * [Related Projects](#related-projects)
   * [Things to Look At](#things-to-look-at)


## What is this?

This project provides packaging of the core *JupyterHub* components, so they can be easily installed on Debian-like target hosts.
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
limited to the current LTS version range (that is 10.x or 8.x as of this writing).
In practice, that means you should use the
[NodeSource](https://github.com/nodesource/distributions#nodesource-nodejs-binary-distributions)
packages to get *Node.js*,
since the native *Debian* ones are typically dated (*Stretch* comes with  ``4.8.2~dfsg-1``).
Adapt the ``debian/control`` file if your requirements are different.

To add any plugins or other optional *Python* dependencies, list them in ``install_requires`` in ``setup.py`` as usual
– but only use versioned dependencies so package builds are reproducible.
These packages are then visible in the default Python3 kernel.
Or add a ``requirements.txt`` file, which has the advantage that you don't need to change any git-controlled files.

Some standard extensions are already contained in ``setup.py`` as setuptools *extras*.
The ``viz`` extra installs ``seaborn`` and ``holoviews``,
which in turn pulls large parts of the usual data science stack,
including ``numpy``, ``scipy``, ``pandas``, and ``matplotlib``.
The related ``vizjs`` extra adds several Javascript-based frameworks like ``bokeh``,
and image rendering support for SVG/PNG writing.
Activating extras increases the package size by 10s or even 100s of MiB,
so be aware of that and keep an eye on package size.

Activate the ``spark`` extra to get PySpark and related utilities.
The systemd unit already includes support for auto-detection or explicit configuration
of an installed JVM.

To activate extras, you need ``dh-virtualenv`` v1.1 which supports the
[--extras](https://dh-virtualenv.readthedocs.io/en/latest/usage.html#cmdoption-extras) option.
That option is used as part of the ``EXTRA_REQUIREMENTS`` variable in ``debian/rules``
– add or remove extras there as you see fit.
There are two special extras named ``default`` and ``full``
– the ``DEFAULT_EXTRAS`` are listed in ``setup.py``, and ``full`` is simply everything.


## “Devops Intelligence” showcase

Here is an example of what you can do using this package, without any great investment of effort or capital. Within a simple setup adding a single JupyterHub host, you can use the built-in Python3 kernel to access existing internal data sources (see figure below).

Such a setup supports risk analysis and decision making within development and operations processes – typical business intelligence / data science procedures can be applied to the ‘business of making and running software’. The idea is to create feedback loops, and facilitate human decision making by automatically providing reliable input in form of up-to-date facts. After all development is our business — so let's have KPIs for developing, releasing, and operating software.

> ![Architecture Overview](https://github.com/1and1/debianized-jupyterhub/raw/master/docs/_static/img/devops-intelligence.png)

See [this notebook](https://nbviewer.jupyter.org/github/jhermann/jupyter-by-example/blob/master/complete-scenarios/devops-intelligence.ipynb)
or [this blog post](https://blog.jupyter.org/devops-intelligence-3ff48a76b525)
for more details and a concrete example of how to use such a setup.


## How to build and install the package

### Building in a Docker container

The easiest way to build the package is using the provided ``Dockerfile.build``.
Then you do not need to install tooling and build dependencies on your machine,
and the package gets built in a pristine environment.
The only thing you need on your workstatioon is a ``docker-ce`` installation of version 17.06 or higher
(either on [Debian](https://docs.docker.com/install/linux/docker-ce/debian/)
or on [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)).

Call ``./build.sh debian:stretch`` to build the package for *Debian Stretch*
– building for *Ubuntu Bionic* with ``./build.sh ubuntu:bionic`` is also supported.
See [Building Debian Packages in Docker](https://dockyard.readthedocs.io/en/latest/packaging-howto.html#dpkg-in-docker)
for more details.

To test the resulting package, read the comments at the start of ``Dockerfile.run``.
Generated package files are placed in the ``dist/`` directory.


### Building directly on your workstation

Otherwise, you need a build machine with all build dependencies installed, specifically
[dh-virtualenv](https://github.com/spotify/dh-virtualenv) in addition to the normal Debian packaging tools.
You can get it from [this PPA](https://launchpad.net/~spotify-jyrki/+archive/ubuntu/dh-virtualenv),
the [official Ubuntu repositories](http://packages.ubuntu.com/search?keywords=dh-virtualenv),
or [Debian packages](https://packages.debian.org/source/sid/dh-virtualenv).

This code requires and is tested with ``dh-virtualenv`` v1.1
– depending on your platform you might get an older version via the standard packages.
See the [dh-virtualenv documentation](https://dh-virtualenv.readthedocs.io/en/latest/tutorial.html#step-1-install-dh-virtualenv) for details.

With tooling installed,
the following commands will install a *release* version of `jupyterhub` into `/opt/venvs/jupyterhub/`.

```sh
git clone https://github.com/1and1/debianized-jupyterhub.git
cd debianized-jupyterhub/
# or "pip download --no-deps --no-binary :all: debianized-jupyterhub" and unpack the archive

sudo apt-get install build-essential debhelper devscripts equivs

sudo mk-build-deps --install debian/control
( deactivate; dpkg-buildpackage -uc -us -b )
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

See the [related section](https://dh-virtualenv.readthedocs.io/en/latest/trouble-shooting.html#pkg-resources-not-found-or-similar)
in the dh-virtualenv manual.


### 'no such option: --no-binary' during package builds

This package needs a reasonably recent `pip` for building.
To upgrade `pip` (which makes sense anyway if your system is still on the ancient version 1.5.6),
call ``sudo python3 -m pip install -U pip``.

When using `dh-virtualenv 1.1` or later releases, this problem should not appear anymore.


### “Unknown lvalue 'ProtectControlGroups' in section 'Service'” at runtime

This appears in the service logs (`journalctl`) when you use the provided systemd unit files
on older systems (e.g. Xenial). They're just warnings, and can be safely ignored.


## Updating requirements

As previously mentioned, additional packages are listed in ``setup.py``.
General dependencies can be found in ``install_requires``,
while groups of optional extensions are part of ``extras_require``.

To assist upgrading to newer versions, call these commands in the project workdir:

```sh
./setup.py egg_info
pip-upgrade --skip-package-installation --skip-virtualenv-check debianized_jupyterhub.egg-info/requires.txt <<<"q"
```

This will list any available newer version numbers, that you can then edit into ``setup.py``.


## How to set up a simple service instance

After installing the package, [JupyterHub](https://jupyterhub.readthedocs.io/) is launched by default
and available at http://127.0.0.1:8000/.

The same is true when you used the ``docker run`` command as mentioned in ``Dockerfile.run``.
The commands as found in ``Dockerfile.run`` also give you a detailed recipe for a manual install,
when you cannot use Docker for any reason – the only difference is process control, read on for that.

The package contains a ``systemd`` unit for the service, and starting it is done via ``systemctl``:

```sh
sudo systemctl enable jupyterhub
sudo systemctl start jupyterhub

# This should show the service in state "active (running)"
systemctl status 'jupyterhub' | grep -B2 Active:
```

The service runs as ``jupyterhub.daemon``.
Note that the ``jupyterhub`` user is not removed when purging the package,
but the ``/var/{log,opt,run}/jupyterhub`` directories and the configuration are.

By default, the ``sudospawner`` is used to start a user's notebook process
– for that purpose, the included ``/etc/sudoers.d/jupyterhub`` configuration
allows the ``jupyterhub`` system user to create these on behalf of any user
listed in the ``JUPYTER_USERS`` alias. Unless you change it, that means
all accounts in the ``users`` group.

In case you want to enable a specific user group for the sudo spawner, change the sudoers file like this:

    sed -i.orig~ -e s/%users/%jhub-users/ /etc/sudoers.d/jupyterhub

If you want certain users to have admin access, add them to the set named `c.Authenticator.admin_users`
in `/etc/jupyterhub/jupyterhub_config.py`.

After an upgrade, the service restarts automatically by default
– you can change that using the ``JUPYTERHUB_AUTO_RESTART`` variable in ``/etc/default/jupyterhub``.

In case of errors or other trouble, look into the service's journal with…

```sh
journalctl -eu jupyterhub
```

To identify your instance, and help users use the right login credentials,
add something similar to this to your `/etc/jupyterhub/jupyterhub_config.py`
(see [this issue](https://github.com/jupyterhub/jupyterhub/pull/1913) for details):

```py
c.JupyterHub.template_vars = dict(
    announcement=
        '<a href="https://confluence.example.com/x/123456" target="_blank">'
        "<h1>DevOps Intelligence Platform</h1></a>",
    announcement_login=
        '<a href="https://confluence.example.com/x/123456" target="_blank">'
        "<h1>DevOps Intelligence Platform</h1></a>",
        "<big>&#128274; <b>Use your company LDAP credentials!</b></big>",
)
```

If you add a PNG image at `/etc/jupyterhub/banner.png`, it is used instead
of the original banner image (sized 208 × 56 px). Note that this is done
via a `postinst` script, so you must call `dpkg-reconfigure jupyterhub`
if you change or add such an image *after* the package installation.


## Securing your JupyterHub web service with an SSL off-loader

Note that JupyterHub can directly offer an SSL endpoint,
but there are a few reasons to do that via a local proxy:

 * JupyterHub needs no special configuration to open a low port (remember, we do not run it as ``root``).
 * Often there are already configuration management systems in place that,
   for commodity web servers and proxies, seamlessly handle certificate management and other complexities.
 * You can protect sensitive endpoints (e.g. metrics) against unauthorized access using
   the built-in mechanisms of the chosen SSL off-loader.

To hide the HTTP endpoint from the outside world,
change the bind URL in ``/etc/default/jupyterhub`` as follows:

    # Bind to 127.0.0.1 only
    sed -i.orig~ -e s~//:8000~//127.0.0.1:8000~ /etc/default/jupyterhub

Restart the service and check that port 8000 is bound to localhost only:

    systemctl restart jupyterhub.service
    netstat -tulpn | grep :8000

Then install your chosen webserver / proxy for SSL off-loading,
listening on port 443 and forwarding to port 8000.
Typical candidates are NginX, Apache httpd, or Envoy.
For an internet-facing service, consider [https-portal](https://github.com/SteveLTN/https-portal),
which is a NginX docker image with easy configuration and built-in *Let's Encrypt* support.

Otherwise, install the Debian `nginx-full` package and copy
[docs/examples/nginx-jhub.conf](https://github.com/1and1/debianized-jupyterhub/blob/master/docs/examples/nginx-jhub.conf)
to the `/etc/nginx/sites-enabled/default` file (or another path depending on your server setup).
Make sure to read through the file, most likely you have to adapt the certificate paths in
`ssl_certificate` and `ssl_certificate_key` (and create a certificate, e.g. a self-signed one).

You also need to create Diffie-Hellman parameters using the following command,
which can take several minutes to finish:

    openssl dhparam -out /etc/ssl/private/dhparam.pem 4096

Then (re-)start the `nginx` service and try to login.

:bangbang: Note that this does not protect against any local users
and their notebook servers and terminals, at least as long as you
use the default spawner that launches local processes.


## Changing the Service Unit Configuration

The best way to change or augment the configuration of a *systemd* service
is to use a ‘drop-in’ file.
For example, to increase the limit for open file handles
above the default of 8192, use this in a **``root``** shell:

```sh
unit='jupyterhub'

# Change max. number of open files for ‘$unit’…
mkdir -p /etc/systemd/system/$unit.service.d
cat >/etc/systemd/system/$unit.service.d/limits.conf <<'EOF'
[Service]
LimitNOFILE=16384
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

A few configuration parameters are set in the ``/usr/sbin/jupyterhub-launcher`` script
and thus override any values provided by ``jupyterhub_config.py``.

 :information_source: Please note that the files in ``/etc/jupyterhub``
 are *not* world-readable, since they might contain passwords.


## Data Directories

 * ``/var/log/jupyterhub`` – Extra log files.
 * ``/var/opt/jupyterhub`` – Data files created during runtime (``jupyterhub_cookie_secret``, ``jupyterhub.sqlite``, …).
 * ``/run/jupyterhub`` – PID file.

You should stick to these locations, because the maintainer scripts have special handling for them.
If you need to relocate, consider using symbolic links to point to the physical location.


## References

### Documentation Links

These links point to parts of the documentation especially useful for operating a JupyterHub installation.

 * [Troubleshooting](https://jupyterhub.readthedocs.io/en/stable/troubleshooting.html#troubleshooting)

   * [Troubleshooting Commands](https://jupyterhub.readthedocs.io/en/stable/troubleshooting.html#troubleshooting-commands)


### Related Projects

 * [Springerle/debianized-pypi-mold](https://github.com/Springerle/debianized-pypi-mold) – Cookiecutter that was used to create this project.

### Things to Look At

 * [Tutorial: Getting Started with JupyterHub](https://jupyterhub-tutorial.readthedocs.io/)
 * https://github.com/jupyterhub/the-littlest-jupyterhub
 * Notebook culling: https://github.com/jupyterhub/jupyterhub/issues/2032
 * https://github.com/jupyterhub/systemdspawner
   * As for “Simple sudo rules do not help, since unrestricted access to systemd-run is equivalent to root”, sudo command patterns or a wrapper script could probably fix that.
 * [Dockerize and Kerberize Notebook for Yarn and HDFS](https://www.youtube.com/watch?v=7m9VK0kXdcM&feature=youtu.be) [YouTube]
   * [bloomberg/jupyterhub-kdcauthenticator](https://github.com/bloomberg/jupyterhub-kdcauthenticator) – A Kerberos authenticator module for the JupyterHub platform.
   * [jupyter-incubator/sparkmagic](https://github.com/jupyter-incubator/sparkmagic) – Jupyter magics and kernels for working with remote Spark clusters.
   * [Apache Livy](https://github.com/apache/incubator-livy#apache-livy) – An open source REST interface for interacting with Apache Spark from anywhere.
 * [jupyter/docker-stacks](https://github.com/jupyter/docker-stacks) – Ready-to-run Docker images containing Jupyter applications.
 * [jupyter/repo2docker](https://github.com/jupyter/repo2docker) – Turn git repositories into Jupyter-enabled Docker Images.
 * [vatlab/SoS](https://github.com/vatlab/SOS) – Workflow system designed for daily data analysis.
 * [sparklingpandas/sparklingpandas](https://github.com/sparklingpandas/sparklingpandas) – SparklingPandas builds on Spark's DataFrame class to give you a polished, pythonic, and Pandas-like API.
 * [data-8/nbzip](https://github.com/data-8/nbzip) – Zips and downloads all the contents of a Jupyter notebook.
 * [data-8/nbgitpuller](https://github.com/data-8/nbgitpuller)  – One-way git pull with auto-merging, most suited for classroom settings.
