# TODOs

## WIP

 * New release


## Ready

 * Sample nginx config
   * https://github.com/jupyterhub/jupyterhub/issues/2105
 * [cull_idle_servers](https://jupyterhub.readthedocs.io/en/stable/getting-started/services-basics.html)


## Backlog

 * Inject a user's "--user" installs into the launched notebook servers
   * https://github.com/jupyterhub/jupyterhub/issues/2136
   * Or https://nbviewer.jupyter.org/github/jhermann/jupyter-by-example/blob/master/setup/configuration.ipynb#Embedded-Dependency-Installation
 * Add JupyterLab (as an option?)
 * Prometheus monitoring → https://github.com/jupyterhub/jupyterhub/issues/2049
   * Graphite bridge: https://github.com/prometheus/client_python#bridges

 * Add a debug switch to the default file
   * https://github.com/jupyterhub/jupyterhub/wiki/Debug-Jupyterhub
 * Add a global ``jupyter_notebook_config.py``
 * https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html


## Maybe

 * Run the proxy as a separate systemd service?
 * Replace CHP by Træfik, an F5 integration, or similar?
   * https://github.com/jupyterhub/traefik-proxy
