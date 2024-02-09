# PWP SPRING 2024
# Ranking API
# Group information
* Student 1. Rainer Laaksonen  Rainer.Laaksonen@oulu.fi
* Student 2. Juho Bruun  Juho.Bruun@student.oulu.fi
* Student 3. Niko Mätäsaho  Niko.Matasaho@student.oulu.fi

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


## Requirements

The minimum Python version supported is 3.8. External library dependencies are:

- Flask 3.0.2
- Flask-SQLAlchemy 3.1.1

The simplest way to install requirements for chosen environment is by command 
`python -m pip install -r requirements.txt`.

## Running the application

This application uses factory methods for the server creation. A ready-to-use Flask object for the Ranking API can be 
retrieved by calling method `create_app` from module `ranking_api.app`. A factory method pattern initializes the 
flask app and creates database and tables if they do not exist yet. The most convenient way for running the app is to 
use `wsgi.py`:

### For development

Run `wsgi.py` as the main module or call `flask --app "wsgi:create_app() run --debug"`

### For production

Call `wsgi:create_app()` with chosen WSGI server application.
