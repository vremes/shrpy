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
```
## Configuration
shrpy looks for config values from OS environment variables.

You can set these environment variables in [.env_example](https://github.com/vremes/shrpy/blob/master/.env_example) and then rename the `.env_example` to `.env`.

| Key | Type | Default value | Description |
| ------ | ------ | ------ | ------ |
| `FLASK_SECRET` | `str` |  `None` | Secret key for Flask application, see https://flask.palletsprojects.com/en/2.0.x/config/#SECRET_KEY |
| `MAX_CONTENT_LENGTH` | `int` | `16777216` | Maximum upload size in bytes, see https://flask.palletsprojects.com/en/2.0.x/config/#MAX_CONTENT_LENGTH |
| `UPLOAD_DIR` | `str` | `/app/uploads/` | Path for uploaded files. |
| `ALLOWED_EXTENSIONS` | `str` | `png;jpg;jpeg;gif;webm;mp4;webp;txt;m4v` | Allowed file extensions separated by semicolon. |
| `UPLOAD_PASSWORD` | `str` | `None` | The password to protect `/api/upload` and `/api/shorten` endpoints. |
| `DISCORD_WEBHOOKS` | `str` | `None` | Discord webhook URLs separated by semicolon. |
| `DISCORD_WEBHOOK_TIMEOUT` | `int` | `5` | Timeout for Discord webhook requests in seconds. |
| `MAGIC_BUFFER_BYTES` | `int` | `2048` | The amount of bytes `python-magic` will read from uploaded file to determine its extension. |
| `FILE_TOKEN_BYTES` | `int` | `12` | The amount of bytes `secrets.token_urlsafe` will use to generate filenames. |
| `URL_TOKEN_BYTES` | `int` | `6` | The amount of bytes `secrets.token_urlsafe` will use to generate shortened URLs. |
| `ORIGINAL_FILENAME_LENGTH` | `int` | `18` | The amount of characters which will be appended to random filename from original filename when `X-Use-Original-Filename` header value is set to `1`. |
| `LOGGER_FILE_NAME` | `str` | `shrpy.log` | Filename for log file. |
| `LOGGER_FILE_PATH` | `str` | `/app/logs/` | Path for log file. |
| `LOGGER_MAX_BYTES` | `int` | `8388608` | The maximum size of log file in bytes. |
| `LOGGER_BACKUP_COUNT` | `int` | `5` | The amount of log files to backup. |

## HTTP Headers

| Name | Example value | Description |
| ------ | ------ | ------ |
`Authorization` | `hunter2` | The plaintext password for file uploads and URL shortening, simply ignore this header if you don't use a password. |
|`X-Use-Original-Filename` | `0` | Allows you to decide if you want to include the file's original filename when saving uploaded files, this is enabled by default, set the value to `0` to disable. |
