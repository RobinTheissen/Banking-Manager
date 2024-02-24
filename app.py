from datetime import timedelta
from data.customer import Customer
from flask import Flask, render_template, request, session, redirect, url_for
import json
import psycopg2
import os


app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=60)  # sets the time for data stored to 60 minutes
app.secret_key = 'geheim'


@app.route('/', methods=['GET', 'POST'])
def index():  # Startseite
    customer_name = ""
    if request.method == 'POST':
        print(session['customer'])
        if session['customer']:
            customer_name = session['customer'][0] + " " + session['customer'][1]
            session['customer'] = None
            return render_template('index.html', customer_name=customer_name)
    else:
        return render_template('index.html', customer_name=customer_name)

    return render_template('index.html', customer_name=customer_name)



@app.route('/register', methods=['GET', 'POST'])
def register():
    customer = Customer
    error = ""
    if request.method == 'POST':
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"]
        )

        cur = conn.cursor()

        # Überprüfe, ob die E-Mail bereits in der Datenbank vorhanden ist
        cur.execute('SELECT COUNT(*) FROM customers WHERE email = %s', (request.form['email'],))
        existing_email_count = cur.fetchone()[0]

        if existing_email_count > 0:
            # Die E-Mail ist bereits in der Datenbank vorhanden, zeige eine Fehlermeldung
            error = "Die E-Mail ist bereits registriert. Bitte verwende eine andere E-Mail-Adresse."

        elif not (len(request.form['password']) >= 8 and
                any(char.isupper() for char in request.form['password']) and
                any(char.islower() for char in request.form['password']) and
                any(char.isdigit() for char in request.form['password']) and
                any(char in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`' for char in request.form['password']) and
                request.form['password'][0] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`' and
                request.form['password'][-1] not in '!@#$%^&*()-_=+[]{}|;:\'",.<>?/~`'):
            error = ("Das Passwort sollte mindestens acht Zeichen, einen Großbuchstaben, einen Kleinbuchstaben, "
                     "sowie ein Sonderzeichen besitzen. Dabei darf das Sonderzeichen nicht am Anfang oder am Ende des "
                     "Passworts stehen.")

        else:
            # Die E-Mail ist noch nicht in der Datenbank vorhanden, füge den Kunden hinzu
            customer = Customer(
                request.form['firstname'],
                request.form['lastname'],
                request.form['age'] if request.form['age'] else None,
                request.form['email'],
                request.form['password'],
                request.form['bankinginstitution'] if request.form['bankinginstitution'] else None
            )

            cur.execute('INSERT INTO customers (firstname, lastname, email, password, age, bankinginstitution)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (customer.fName, customer.lName, customer.email, customer.pw, customer.age, customer.bankingInst))
            conn.commit()

        cur.close()
        conn.close()

        # Wenn ein Fehler auftritt, kehre zur Registrierungsseite mit Fehlermeldung zurück
        if error:
            return render_template("register.html", error=error)
        # Erfolgreich registriert, leite den Benutzer zu einer anderen Seite weiter
        else:
            session['customer'] = [customer.fName, customer.lName, customer.email, customer.pw, customer.age, customer.bankingInst]
            return redirect(url_for('success_page'))

    return render_template("register.html")


@app.route('/success', methods=['GET', 'POST'])
def success_page():
    print(session['customer'])
    return render_template('success.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']

        conn = psycopg2.connect(
                    host='localhost',
                    database='postgres',
                    user=os.environ["DB_USERNAME"],
                    password=os.environ["DB_PASSWORD"]
                )

        cur = conn.cursor()

        cur.execute('SELECT * FROM customers WHERE email = %s AND password = %s',
                    (login_email, login_password))
        existing_customer = cur.fetchone()[1:]
        if existing_customer:
            session['customer'] = existing_customer
            print(session['customer'])
            return redirect(url_for('success_page'))
        else:
            error = 'Bitte überprüfe die eingegebenen Daten'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    if request.method == 'POST':
        return render_template('index.html')
    else:
        return render_template('logout.html')
