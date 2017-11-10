#!/bin/bash

ln -s /etc/nginx/sites-available/hapra /etc/nginx/sites-enabled/hapra
rm /etc/nginx/sites-enabled/default
echo "Would you like to use HTTP Basic Auth?[y/N]"
read auth
if [ $auth == y ]; then
	mv hapra_auth.nginx /etc/nginx/sites-available/hapra
	echo "Username: "
	read username
	echo "Password: "
	read password
	$password_hash = {openssl passwd -apr1 $password}
	echo $password_hash
	echo -n "${username}:" >> /etc/nginx/.htpasswd
	echo -n "$(openssl passwd -apr1 $password_hash)" >> /etc/nginx/.htpasswd
else
	mv hapra.nginx /etc/nginx/sites-available/hapra
fi
