[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/alerts/)

[ShareX](https://getsharex.com/) custom uploader/destination server written in Python (Flask).

I created this mostly for my personal use, but if you have any suggestions, ideas or improvements feel free to open a new issue (pull requests are also welcome).

ShareX URL shortening config is available at `/api/sharex/shorten`.

ShareX upload config is available at `/api/sharex/upload`.

# Setup (NGINX, Gunicorn, Supervisor)
1. Install NGINX and Supervisor:  
`apt install nginx supervisor`
3. Install Gunicorn and Gevent:  
`pip3 install gunicorn gevent`
4. Clone the repository:  
`git clone https://github.com/vremes/shrpy.git /var/www/shrpy/`
6. Install requirements:  
`pip3 install -r /var/www/shrpy/requirements.txt`
7. Setup environment variables:  
`cd /var/www/shrpy/app/`  
`cp .env_example .env`  
`nano .env` and set `FLASK_SECRET` to secret string, e.g. `FLASK_SECRET="XYZ"`  
9. Configure supervisor to run gunicorn:  
`nano /etc/supervisor/conf.d/shrpy.conf`
```
[program:shrpy]
directory=/var/www/shrpy
command=gunicorn --bind=127.0.0.1:8000 --worker-class=gevent wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/shrpy.err.log
stdout_logfile=/var/log/shrpy.out.log
```
7. Update supervisor and configure NGINX:  
`supervisorctl update`  
`nano /etc/nginx/sites-available/shrpy.conf`  
```nginx
server {
    listen 80;
    server_name example.com; # <==== Change to your domain name
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
8. Enable NGINX config and restart:  
`ln -s /etc/nginx/sites-available/shrpy.conf /etc/nginx/sites-enabled/`  
`service nginx restart`  
8. Visit `/api/sharex/upload` or `/api/sharex/shorten` route on your domain and it should be running
```json
{
        "Body":"MultipartFormData",
        "DeletionURL":"$json:delete_url$",
        "DestinationType":"ImageUploader, FileUploader",
        "ErrorMessage":"$json:status$",
        "FileFormName":"file",
        "Headers":{
            "Authorization":"YOUR-UPLOAD-PASSWORD-HERE",
            "X-Use-Original-Filename":1
        },
        "Name":"example.com (File uploader)",
        "RequestMethod":"POST",
        "RequestURL":"http://example.com/api/upload",
        "URL":"$json:url$",
        "Version":"1.0.0"
}
```
---
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
