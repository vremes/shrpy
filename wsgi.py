import os
from app import create_app
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# WSGI instance
application = create_app()

# Get secret from OS environment
application.secret_key = os.getenv('FLASK_SECRET')

if __name__ == '__main__':
    application.secret_key = 'dev'
    application.debug = True
    application.run()
