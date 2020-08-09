# flask-sharex
Minimal [ShareX](https://getsharex.com/) custom uploader written in Python (Flask).

ShareX custom uploader configuration is available at `/api/sharex` route.

# Setup
1. Install requirements: `pip3 install -r requirements.txt`
2. Use WSGI server and web server of your choice to deploy it, i use [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/), [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) is a nice tutorial
* If you want to run Flask development server, simply type `python3 wsgi.py`
