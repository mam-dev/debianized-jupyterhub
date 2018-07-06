# House-keeping cron job

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root@localhost

# TODO: REMOVE THE : BEFORE THE /usr/bin COMMAND TO ACTUALLY RUN THE JOB!
# Also adapt the arguments to the task at hand.
# Or simply remove this file.

# m h   dom mon dow   user        command
7 0     *   *   *     jupyterhub      . /etc/default/jupyterhub && : /usr/bin/jupyterhub maintenance >/var/log/jupyterhub/cron.log 2>&1
