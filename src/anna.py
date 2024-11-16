from flask import Blueprint, render_template, request

# Define 'anna' as a Blueprint
anna = Blueprint('anna', __name__)

@anna.route("/")
def about():
    return "<p>Hello, world!<p>"