from flask import Blueprint, render_template, request

# Define 'anna' as a Blueprint
lara = Blueprint('lara', __name__)

@lara.route("/lara")
def about():
    return "<p>Hello, Lara!<p>"

@lara.route("/login")
def logInPage():
    return render_template("logInPage.html")

@lara.route("/requests")
def requestsPage():
    return render_template("makeRequests.html")

@lara.route("/signup")
def signUpPage():
    return render_template("signUpPage.html")