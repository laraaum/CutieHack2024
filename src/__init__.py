from flask import Flask


def create_app():
    app = Flask(__name__)

    app.static_folder = 'static'

    # Import and register the Blueprint
    from .anna import anna
    app.register_blueprint(anna, url_prefix='/')

    from .lara import lara
    app.register_blueprint(lara, url_prefix='/')

    return app


