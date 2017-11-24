# hapra
A RESTful API for HAProxy Load Balancer

## Installation

You can install hapra to you local machine or to a Docker container.

### Docker Installation

#### Dependencies

For this method, all you need on your local machine is Docker and
HAProxy 1.7(Other versions are not tested and probably will **NOT** work
properly.). Check your distributions repositories for native packages or
Docker Documentation for installation process on different
distributions.

#### Installation

Navigate to applications top directory and use `docker build` with
provided Dockerfile. You can use whatever `<image_name>` you like.

```
# docker build -t <image_name> .
```

This application also has a configuration file, `hapra.cfg`. Right now
only supported configuration is `READ_ONLY` which is set to `True` by
default. This file will be located at `/etc/hapra.cfg` in the Docker
container. You can edit the Dockerfile to change this location.

Then use `docker run` to run the image you just built. You can use
whatever `<container_name>` you like. This command assumes that your
haproxy stat socket is located at `/var/lib/haproxy/` directory. If
your socket is at another directory, you need to change this command
*and* `main/functions.py` file accordingly since this path is hardcoded
there. `USER` and `PASSWD` environment variables are used for HTTP
Basic Authentication.

```
# docker run --name <container_name> --volume "/var/lib/haproxy/:/var/lib/haproxy/:rw" -d -p 81:81 -e USER=<username> -e PASSWD=<password> <image_name>
```

### Local Installation

#### Dependencies

Python, Flask, Nginx and uWSGI are required. It's recommended to use
pip and virtualenv for installation of python packages.

Dependency installation for Ubuntu:

```
# apt-get update
# apt-get install python-dev python-pip nginx
# pip install virtualenv
```

#### Installation

Navigate to parent directory of the application. Preferably, create an
empty directory, move application directory inside of new empty
directory and navigate to that directory.

Create a virtual environment in that directory. You can use any name
you like in place of `hapraenv`. Then activate the environment:

```
$ virtualenv hapraenv
$ source hapraenv/bin/activate
```

Install remaining python packages using this virtual environment:

```
(hapraenv) $ pip install uwsgi flask
```

You can use a systemd unit file to start the application at every boot.

A configuration file, `hapra.cfg`, is also provided with the
application. Right now, it only supports a `READ_ONLY` option which is
set to `True` by default. This configuration file is necessary for the
application to work, so you need to pass it's location as an
environment variable in the unit file.

```
[Unit]
Description=uWSGI instance to serve hapra
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/<path-to-hapra-directory>
Environment="PATH=/<path-to-hapraenv-directory>/bin"
Environment="CONFIG_FILE=/<path-to-your-hapra-config-file>"
ExecStart=/<path-to-hapraenv-directory>/bin/uwsgi --ini hapra.ini

[Install]
WantedBy=multi-user.target
```

Copy or symlink your unit file to `/etc/systemd/system/hapra.service`:

```
# cp /<path-to-your-unit-file> /etc/systemd/system/hapra.service
```
or
```
# ln -s /<path-to-your-unit-file> /etc/systemd/system/hapra.service
```

Start and enable service:
```
# systemctl start myproject
# systemctl enable myproject
```

Now you need to configure Nginx. You can copy one of the given
configuration files, or make your own configuration.

If you need HTTP Basic Authentication, copy `hapra_auth.nginx` file to `/etc/nginx/sites-available/`:

```
# cp /<path-to-your-hapra_auth.nginx-file> /etc/nginx/sites-available/hapra
```
You should also create a password file for this to work:


Else, copy `hapra.nginx` to same `/etc/nginx/sites-available/`:

```
# cp /<path-to-your-hapra.nginx-file> /etc/nginx/sites-available/hapra
```

Then create a symlink in `/etc/nginx/sites-enabled/`:

```
# ln -s /etc/nginx/sites-available/hapra /etc/nginx/sites-enabled/hapra
```

Contents of the files for those who want to create their own configurations:

`hapra.nginx`:

```
server {
	listen 80;

	location / {
		include uwsgi_params;
		uwsgi_pass unix:/run/hapra.sock;
	}
}
```

`hapra_auth.nginx`:

```
server {
	listen 80;

	location / {
		auth_basic "Restricted Content";
		auth_basic_user_file /etc/nginx/.haprapasswd;
		include uwsgi_params;
		uwsgi_pass unix:/run/hapra.sock;
	}
}
```

Restart nginx service:

```
# systemctl restart nginx
```

Now make sure that HAProxy is running, fire up your browser and browse
to `localhost/hapra/show/stat` and enter your HTTP Basic Auth password
if you set it up. If you see an output in JSON format congratulations,
hapra is working.

## Usage

There is a URL in application for each HAProxy Unix socket command. An
example URL is given below:

Docker installation:
```
http://<container-address>/hapra/show/stat?id=2&sid=5
```

Local installation:
```
http://localhost/hapra/show/stat?id=2&sid=5
```

Each URL starts with `.../hapra/`. `show <...>` commands are formated as
`.../hapra/show/*`, `get <...>` commands are formated as
`.../hapra/get/*`, `set <...>` commands are formated as
`.../hapra/set/*` and so on. You can pass parameters to commands as
query strings.

URL's and their respective socket commands will be documented in a
more detailed manual.
