# TODOs

## WIP

 * Install Pillow from source, to ensure freetype support
 * https://github.com/ipython-contrib/jupyter_contrib_nbextensions/blob/master/src/jupyter_contrib_nbextensions/nbconvert_support/toc2.py

        jupyter contrib nbextension install --only-files --sys-prefix --symlink --debug
        jupyter contrib nbextension install --only-config --system --debug

 * Cull idle servers
   * https://jupyterhub.readthedocs.io/en/stable/getting-started/services-basics.html
   * [Limit Notebook resource consumption by culling kernels - IBM Code](https://developer.ibm.com/code/2017/10/26/limit-notebook-resource-consumption-culling-kernels/)


## Ready

 * Look into "nbreport"
 * https://github.com/quantopian/qgrid
 * https://jupyterhub.github.io/nbgitpuller/link
 * Metrics auth: https://github.com/jupyterhub/jupyterhub/issues/2105


## Backlog

 * [Set Your Jupyter Notebook up Right with this Extension](https://towardsdatascience.com/set-your-jupyter-notebook-up-right-with-this-extension-24921838a332)
 * https://ipywidgets.readthedocs.io/
 * https://github.com/pyviz/param
 * Inject a user's "~/.ipython/lib/…" installs into the launched notebook servers
   * https://github.com/jupyterhub/jupyterhub/issues/2136
   * Or https://nbviewer.jupyter.org/github/jhermann/jupyter-by-example/blob/master/setup/configuration.ipynb#Embedded-Dependency-Installation

        $ cat .ipython/profile_default/startup/README
        This is the IPython startup directory

        .py and .ipy files in this directory will be run *prior* to any code or files specified
        via the exec_lines or exec_files configurables whenever you load this profile.

        Files will be run in lexicographical order, so you can control the execution orderof files
        with a prefix, e.g.::

            00-first.py
            50-middle.py
            99-last.ipy

        cat > ~/.ipython/profile_default/startup/00-user-pkg.py <<'EOF'
        import os, sys
        sys.path.insert(1, os.path.expanduser('~/.ipython/lib/python3.5/site-packages'))
        EOF

 * Add JupyterLab (as an option?)
   * https://github.com/NixOS/nixpkgs/pull/50858
 * Prometheus monitoring → https://github.com/jupyterhub/jupyterhub/issues/2049
   * Graphite bridge: https://github.com/prometheus/client_python#bridges

 * Add a debug switch to the default file
   * https://github.com/jupyterhub/jupyterhub/wiki/Debug-Jupyterhub
 * Add a global ``jupyter_notebook_config.py``
 * https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html


## Maybe

 * https://github.com/erdewit/eventkit
 * https://github.com/nteract/bookstore
 * Run the proxy as a separate systemd service?
 * Replace CHP by Træfik, an F5 integration, or similar?
   * https://github.com/jupyterhub/traefik-proxy
