[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/vremes/shrpy.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/vremes/shrpy/alerts/)

[ShareX](https://getsharex.com/) custom uploader/destination server written in Python (Flask).

I created this mostly for my personal use, but if you have any suggestions, ideas or improvements feel free to open a new issue (pull requests are also welcome).

# Endpoints

| Route | HTTP method | Description |
| ----- | ------ | ------ |
`/` | `GET` | Index page with some text just to make sure this application works. |
`/uploads/<filename>` | `GET` | Route to serve a given file from uploads directory. |
`/url/<token>` | `GET` | Redirects you to the URL for given short URL token. |
`/api/sharex/upload` | `GET` | ShareX custom uploader configuration for files, you can import this to ShareX from **Destinations** -> **Custom uploader settings** -> **Import** -> **From URL** |
`/api/sharex/shorten` | `GET` | ShareX custom uploader configuration for short URLs, you can import this to ShareX from **Destinations** -> **Custom uploader settings** -> **Import** -> **From URL** |
`/api/upload` | `POST` | Route for file uploads. |
`/api/shorten` | `POST` | Route for URL shortening. |
`/api/delete-short-url/<hmac_hash>/<token>` | `GET` | ShareX deletion URL for short URLs. |
`/api/delete-file/<hmac_hash>/<filename>` | `GET` | ShareX deletion URL for files. |

# Setup

Below you'll find two examples on how to setup this application.

### Development
1. Clone the repository
```sh
git clone https://github.com/vremes/shrpy.git
```
2. Move to cloned repository directory and install requirements
```sh
cd shrpy
pip3 install -r requirements.txt
```
3. Setup `.env` file, see [Configuration](#configuration) for additional information
```sh
cp .env_template .env
nano .env
```
  - You **must** set `FLASK_SECRET` to something, good way to generate secrets is the following command
    ```sh
    python -c "from secrets import token_urlsafe; print(token_urlsafe(64))"
    ```
4. Run Flask built-in development server
```sh
python3 wsgi.py
```

### Production
1. Install NGINX and Supervisor
```sh
apt install nginx supervisor
```
2. Install Gunicorn and Gevent
```sh
pip3 install gunicorn gevent
```
3. Clone the repository to `/var/www/`
```sh
git clone https://github.com/vremes/shrpy.git /var/www/shrpy
```
4. Move to cloned repository directory and install requirements
```sh
cd /var/www/shrpy/
pip3 install -r requirements.txt
```
5. Setup `.env` file, see [Configuration](#configuration) for additional information
```sh
cp .env_template .env
nano .env
```
  - You **must** set `FLASK_SECRET` to something, good way to generate secrets is the following command
    ```sh
    python -c "from secrets import token_urlsafe; print(token_urlsafe(64))"
    ```
6. Configure Supervisor to run Gunicorn, see [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/index.html) for additional information
```sh
nano /etc/supervisor/conf.d/shrpy.conf
```
  - Example configuration:
    ```
    [program:shrpy]
    directory=/var/www/shrpy
    command=gunicorn --bind=127.0.0.1:8000 --worker-class=gevent wsgi:application
    autostart=true
    autorestart=true
    stderr_logfile=/var/log/shrpy.err.log
    stdout_logfile=/var/log/shrpy.out.log
    ```
7. Update Supervisor configuration and configure NGINX
```sh
supervisorctl update
nano /etc/nginx/sites-available/shrpy.conf
```
  - Example configuration:
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
8. Enable NGINX configuration and restart NGINX
```sh
ln -s /etc/nginx/sites-available/shrpy.conf /etc/nginx/sites-enabled/
service nginx restart
```
9. Visit the root (`/`) path on your domain and it should be running:
```json
{
    "message": "It works! Beep boop."
}
```
---
## Configuration
shrpy looks for config values from OS environment variables.

You can set these environment variables in [.env_template](https://github.com/vremes/shrpy/blob/master/.env_template) and then rename the `.env_template` to `.env`.

| Key | Type | Default value | Description |
| ------ | ------ | ------ | ------ |
| `FLASK_SECRET` | `str` |  `None` | Secret key for Flask application, see https://flask.palletsprojects.com/en/2.0.x/config/#SECRET_KEY |
| `UPLOAD_DIR` | `str` | `/app/uploads/` | Path for uploaded files. |
| `ALLOWED_EXTENSIONS` | `str` | `png;jpg;jpeg;gif;webm;mp4;webp;txt;m4v` | Allowed file extensions separated by semicolon. |
| `CUSTOM_EXTENSIONS` | `str` | `video/x-m4v=m4v,image/webp=webp` | Additional `mimetype=extension` pairs for Python `mimetypes` module |
| `UPLOAD_PASSWORD` | `str` | `None` | The password to protect `/api/upload` and `/api/shorten` endpoints. |
| `DISCORD_WEBHOOKS` | `str` | `None` | Discord webhook URLs separated by semicolon. |
| `DISCORD_WEBHOOK_TIMEOUT` | `int` | `5` | Timeout for Discord webhook requests in seconds. |
| `MAGIC_BUFFER_BYTES` | `int` | `2048` | The amount of bytes `python-magic` will read from uploaded file to determine its extension. |
| `FILE_TOKEN_BYTES` | `int` | `12` | The amount of bytes `secrets.token_urlsafe` will use to generate filenames. |
| `URL_TOKEN_BYTES` | `int` | `6` | The amount of bytes `secrets.token_urlsafe` will use to generate shortened URLs. |
| `ORIGINAL_FILENAME_LENGTH` | `int` | `18` | The amount of characters which will be appended to random filename from original filename when `USE_ORIGINAL_FILENAME` value is `True`. |
| `USE_ORIGINAL_FILENAME` | `bool` | `True` | If saved files should include original filename.

## HTTP Headers

| Name | Example value | Description |
| ------ | ------ | ------ |
`Authorization` | `hunter2` | The plaintext password for file uploads and URL shortening, simply ignore this header if you don't use a password. |
