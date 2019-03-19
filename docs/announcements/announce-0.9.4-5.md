# [ANN] jupyterhub 0.9.4-5 Debian Package

I released a new version of my Debian packaging for JupyterHub (https://github.com/1and1/debianized-jupyterhub#jupyterhub-debian-packaging). It makes the installation of a fully working hub on a Debian or Ubuntu server easy, with everything already installed and compiled (no build tools needed).

The package comes with a fully equipped Python3 kernel – the scientific Python stack and common visualization frameworks are built in. All additional packages beyond the JupyterHub core are organized into setuptools ‘extras‘. You can select them for inclusion (many are added by default), or remove unneeded ones to reduce the package size, by changing the “debian/rules” file.

On an Ubuntu / Debian workstation, using this package you get readily available notebooks for personal use, without the need to start a notebook server on the command line every time you want to edit a notebook.

Technically, this is a self-contained Python3 venv wrapped into a Debian package (an "omnibus" package, all passengers on board). You can build the package in a Docker container, so that you don't need to worry about installing build dependencies – the Dockerfile does that for you, without affecting your workstation or build host.

For more details, check out the GitHub README (see link above).


Changes since 0.9.4-3:

  * Extras: Added 'docker', 'nlp', 'ml', 'utils', and 'vizjs' (included by default)
  * Extras: Added 'arrow', 'nltk', and 'parquet' (optional)
  * notebook: update to 5.7.6 (CVE-2019–9644); also updated other explicit requirements
  * Tornado: kept at 5.x because of compatibility problems
  * Packaging: Switched to built-in Python3 venv
