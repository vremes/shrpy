from app import create_app

# WSGI instance
application = create_app()

if __name__ == '__main__':
    application.debug = True
    application.run()
