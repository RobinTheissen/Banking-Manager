from datetime import timedelta
from data.customer import Customer
from flask import Flask, render_template, request, session
import json
import psycopg2
import os


app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=60)  # sets the time for data stored to 60 minutes
app.secret_key = 'geheim'


@app.route('/', methods=['GET', 'POST'])
def index():  # Startseite

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        bankinginstitution = request.form['bankinginstitution']

        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"]
        )

        cur = conn.cursor()
        cur.execute('INSERT INTO users (firstname, lastname, email, password, age, bankinginstitution)'
                    'VALUES (%s, %s, %s, %s, %s, %s)',
                    (firstname, lastname, email, password, age, bankinginstitution))
        conn.commit()
        cur.close()
        conn.close()

    return render_template("register.html")  # on server validation error
