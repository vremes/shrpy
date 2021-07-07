import os
from app import create_app

# WSGI instance
application = create_app()

# Get secret from OS environment
application.secret_key = os.getenv('FLASK_SECRET')

if __name__ == '__main__':
    application.secret_key = 'dev'
    application.debug = True
    application.run()
