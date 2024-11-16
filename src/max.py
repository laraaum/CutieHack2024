from flask import Flask, render_template, request
import os

max = Flask(__name__)

@max.route('/', methods=['GET'])
def logInPage():
    return render_template('logInPage.html')