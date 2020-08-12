Minimal [ShareX](https://getsharex.com/) custom uploader written in Python (Flask).

ShareX custom uploader configuration is available at `/api/sharex` route.

# Setup
1. Install requirements: `pip3 install -r requirements.txt`
2. Set `FLASK_SECRET` OS environment variable to something super secret
3. Use WSGI server and web server of your choice to deploy it, i use [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/), [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) is a nice tutorial
* If you want to run Flask development server, simply type `python3 wsgi.py`
---
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
        alias /var/www/flask-sharex-server/app/uploads/;
    }
}
```
## Example [Supervisord](http://supervisord.org/) config
```config
[program:flask-sharex-server]
directory=/var/www/flask-sharex-server
command=gunicorn --bind=127.0.0.1:8000 wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/flask-sharex-server.err.log
stdout_logfile=/var/log/flask-sharex-server.out.log
environment=FLASK_SECRET=""

```
