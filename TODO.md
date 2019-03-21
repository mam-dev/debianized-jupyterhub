# TODOs

## WIP

 * Cull idle servers
   * https://jupyterhub.readthedocs.io/en/stable/getting-started/services-basics.html
   * [Limit Notebook resource consumption by culling kernels - IBM Code](https://developer.ibm.com/code/2017/10/26/limit-notebook-resource-consumption-culling-kernels/)


## Ready

 * Metrics auth: https://github.com/jupyterhub/jupyterhub/issues/2105


## Backlog

 * [Set Your Jupyter Notebook up Right with this Extension](https://towardsdatascience.com/set-your-jupyter-notebook-up-right-with-this-extension-24921838a332)
 * Inject a user's "~/.ipython/lib/…" installs into the launched notebook servers
   * https://github.com/jupyterhub/jupyterhub/issues/2136
   * Or https://nbviewer.jupyter.org/github/jhermann/jupyter-by-example/blob/master/setup/configuration.ipynb#Embedded-Dependency-Installation
 * Add JupyterLab (as an option?)
   * https://github.com/NixOS/nixpkgs/pull/50858
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
