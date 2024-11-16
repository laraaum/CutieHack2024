from flask import Flask, render_template, request
import os

max = Flask(__name__)

@max.route('/', methods=['GET'])
def logInPage():


@max.route('/', methods=['GET'])
def signUpPage():
    return render_template('signUpPage.html')

@max.route('/', methods=['GET'])
def customersDataPage():
    return render_template('customersDataPage.html')

@max.route('/', methods=['GET'])
def makeRequests():
    return render_template('makeRequests.html')