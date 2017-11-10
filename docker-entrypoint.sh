#!/bin/bash

trap 'exit' ERR

#  Default values of environment variables
CONFIG_FILE=${CONFIG_FILE:-/etc/hapra.cfg}

echo -n "${USER}:" >> /etc/nginx/.htpasswd
echo -n "$(openssl passwd -apr1 $PASSWD)" >> /etc/nginx/.htpasswd
sed -i '/location \/ {/ a \        auth_basic "Restricted Content";' /etc/nginx/conf.d/nginx.conf
sed -i '/"Restricted Content"/ a \        auth_basic_user_file /etc/nginx/.htpasswd;' /etc/nginx/conf.d/nginx.conf

if ! [ -z "${READ_ONLY}" ]
  then
	sed -i "s/^READ_ONLY = .*$/READ_ONLY = $READ_ONLY/" $CONFIG_FILE
fi

exec "$@"
