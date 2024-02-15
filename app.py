from datetime import timedelta
from data.customer import Customer
from flask import Flask, render_template, request, session
import json

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=60)  # sets the time for data stored to 60 minutes
app.secret_key = 'geheim'


@app.route('/', methods=['GET', 'POST'])
def index():  # Startseite

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ""
    if request.method == "POST":
        data = request.form
        customer = Customer(
            data.get("vorname"),
            data.get("nachname"),
            data.get("alter"),
            data.get("email"),
            data.get("passwort"),
            data.get("bankingInst"))

    return render_template("register.html", error=error)  # on server validation error
