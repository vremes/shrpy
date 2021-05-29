[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/alerts/)

[ShareX](https://getsharex.com/) custom uploader/destination server written in Python (Flask).

I created this mostly for my personal use, but if you have any suggestions, ideas or improvements feel free to open a new issue (pull requests are also welcome).

# Setup
1. Install requirements: `pip3 install -r requirements.txt`
2. Rename the `.env_example` file to `.env` and set `FLASK_SECRET` to something super secret
3. Use WSGI server of your choice and WSGI-compatible web server to deploy it, for example [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/) ([tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04))
* If you want to run Flask development server, simply type `python3 wsgi.py`

Once deployment is successful, open your ShareX and go to `Destinations` -> `Custom uploader settings` -> `Import` -> `From URL` and enter your URL (e.g. `https://example.com/api/sharex/upload`) then click `OK`.

ShareX URL shortening config is available at `/api/sharex/shorten`.

ShareX upload config is available at `/api/sharex/upload`.

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

`ALLOWED_EXTENSIONS`: A list of allowed file extensions, set this to empty list if you want to allow all file extensions.

`UPLOAD_PASSWORD`: Password (str) for `/api/upload` endpoint, you can leave it to `None` if you do not want to use a password.

`DISCORD_WEBHOOKS`: A list of Discord webhook URLs, leave this to empty list to disable this feature.

`DISCORD_WEBHOOK_TIMEOUT`: Timeout for Discord webhook requests, in seconds.

`MAGIC_BUFFER_BYTES`: The amount of bytes `python-magic` will read from uploaded file to determine its extension, the default value of `2048` should be fine.

`FILE_TOKEN_BYTES`: The amount of bytes `secrets.token_urlsafe` will use to generate filenames.

`URL_TOKEN_BYTES`: The amount of bytes `secrets.token_urlsafe` will use to generate shortened URLs.

`ORIGINAL_FILENAME_LENGTH`: The amount of characters that will be appended to random filename from original filename when `X-Use-Original-Filename` header value is set to `1`.

## Headers

`Authorization`: The password for uploading files (`UPLOAD_PASSWORD` in config.py file), simply ignore this header if you don't use a password.

`X-Use-Original-Filename`: Allows you to decide if you want to include the file's original filename when saving uploaded files, this is enabled by default, set the value to `0` to disable.
