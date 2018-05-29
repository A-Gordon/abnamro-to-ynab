#!/bin/bash
source /data/.env_vars
export PATH=/usr/local/rbenv/shims:/usr/local/rbenv/bin:/usr/local/rbenv/bin:/usr/local/rbenv/shims:/usr/local/rbenv/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
/usr/local/bin/python /src/autoupdater.py
