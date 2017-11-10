#!/bin/bash

rm /etc/nginx/sites-enabled/default
echo "Would you like to use HTTP Basic Auth?[y/N]"
read auth
if [ $auth == y ]; then
	cp hapra_auth.nginx /etc/nginx/sites-available/hapra
	chown root:root /etc/nginx/sites-available/hapra
	rm /etc/nginx/.haprapasswd
	echo "Username: "
	read username
	echo "Password: "
	read password
	echo $password
	echo -n "${username}:" >> /etc/nginx/.haprapasswd
	echo -n "$(openssl passwd -apr1 $password)" >> /etc/nginx/.haprapasswd
else
	cp hapra.nginx /etc/nginx/sites-available/hapra
	chown root:root /etc/nginx/sites-available/hapra
fi
ln -s /etc/nginx/sites-available/hapra /etc/nginx/sites-enabled/hapra
systemctl restart nginx
