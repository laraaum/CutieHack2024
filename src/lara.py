from flask import Blueprint, render_template, request

# Define 'anna' as a Blueprint
lara = Blueprint('lara', __name__)

@lara.route("/lara")
def about():
    return "<p>Hello, Lara!<p>"

@lara.route("/login")
def logInPage():
    return render_template("logInPage.html")