[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/alerts/)


Minimal [ShareX](https://getsharex.com/) custom uploader written in Python (Flask).

ShareX custom uploader configuration is available at `/api/sharex` route.

I created this mostly for my personal use, but if you have any suggestions, ideas or improvements feel free to submit a new issue!

# Setup
1. Install requirements: `pip3 install -r requirements.txt`
2. Set `FLASK_SECRET` OS environment variable to something super secret
3. Use WSGI server and web server of your choice to deploy it, i use [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/), [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) is a nice tutorial
* If you want to run Flask development server, simply type `python3 wsgi.py`

## Example NGINX config
```nginx
server {
    listen 80;
    server_name mydomain.com;
    client_max_body_size 16M;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }

    location /uploads {
        alias /var/www/shrpy/app/uploads/;
    }
}
```
## Example [Supervisord](http://supervisord.org/) config
```config
[program:shrpy]
directory=/var/www/shrpy
command=gunicorn --bind=127.0.0.1:8000 wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/shrpy.err.log
stdout_logfile=/var/log/shrpy.out.log
environment=FLASK_SECRET="PLEASE-CHANGE-THIS"
```
