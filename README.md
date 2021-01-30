[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/alerts/)

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/vremes/shrpy/tree/master)

[ShareX](https://getsharex.com/) custom uploader/destination server written in Python (Flask).

I created this mostly for my personal use, but if you have any suggestions, ideas or improvements feel free to open a new issue.

# Setup
1. Install requirements: `pip3 install -r requirements.txt`
2. Set `FLASK_SECRET` OS environment variable to something super secret
3. Use WSGI server and web server of your choice to deploy it, i use [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/), [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) is a nice tutorial
* If you want to run Flask development server, simply type `python3 wsgi.py`

Once deployment is successful, open your ShareX and go to `Destinations` -> `Custom uploader settings` -> `Import` -> `From URL` and enter your URL (e.g. `https://example.com/api/sharex`) then click `OK`.

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
    
    # Optional headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header Content-Security-Policy "default-src 'self';";
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
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
## Configuration
Config file is located in [/app/config.py](/app/config.py)

`MAX_CONTENT_LENGTH`: File upload limit, in bytes.

`UPLOAD_DIR`: Path to the directory where uploaded files will be saved to.

`ALLOWED_EXTENSIONS`: A list of allowed file extensions.

`UPLOAD_PASSWORD`: Password (str) for `/api/upload` endpoint, you can leave it to `None` if you do not want to use a password.

`DELETE_THRESHOLD_DAYS`: Automatically delete the files in `UPLOAD_FOLDER` that are older than the specified value (in days), leave this to `0` if you want to disable this feature.

## Headers

`Authorization`: The password for uploading files (`UPLOAD_PASSWORD` in config.py file), simply ignore this header if you don't use a password.

`X-Use-Original-Filename`: Allows you to decide if you want to include the file's original filename when saving uploaded files, this is enabled by default, set the value to `0` to disable.
