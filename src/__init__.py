from flask import Flask


def create_app():
    app = Flask(__name__)

    # Import and register the Blueprint
    from .anna import anna
    app.register_blueprint(anna, url_prefix='/')

    return app


