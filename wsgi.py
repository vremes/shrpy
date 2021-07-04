import os
from environs import Env
from app import create_app

# Load .env file
env = Env()
env.read_env()

# WSGI instance
application = create_app()

# Get secret from OS environment
application.secret_key = os.getenv('FLASK_SECRET')

if __name__ == '__main__':
    application.secret_key = 'dev'
    application.debug = True
    application.run()
