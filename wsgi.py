"""
Module for starting the application. Either run this module as the main module for development mode
or call the create_app method to get a ready-to-use Flask object for Ranking API.
"""
from ranking_api.app import create_app


if __name__ == "__main__":
    from config import Config
    app_config = Config()
    app_config.DEBUG = True
    app = create_app(app_config)
    app.run()
