from datetime import timedelta, datetime
from data.customer import Customer
from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
import os

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=60)  # sets the time for data stored to 60 minutes
app.secret_key = 'geheim'


@app.route('/', methods=['GET', 'POST'])
def index():  # Startseite
    customer_name = ""
    if request.method == 'POST':
        if session == {}:
            return render_template('index.html')
        else:
            customer_name = session['customer'][1] + " " + session['customer'][2]
            session.clear()
            return render_template('index.html', customer_name=customer_name)

    else:
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
                        (customer.fName, customer.lName, customer.email, customer.pw, customer.age,
                         customer.bankingInst))
            conn.commit()
            cur.execute('SELECT customerid FROM customers WHERE email = %s',
                        (customer.email,))
            customer_id = cur.fetchone()[0]

        cur.close()
        conn.close()

        # Wenn ein Fehler auftritt, kehre zur Registrierungsseite mit Fehlermeldung zurück
        if error:
            return render_template("register.html", error=error)
        # Erfolgreich registriert, leite den Benutzer zu einer anderen Seite weiter
        else:
            session['customer'] = [customer_id, customer.fName, customer.lName, customer.email, customer.pw, customer.age,
                                   customer.bankingInst]
            return redirect(url_for('create_account'))

    return render_template("register.html")


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
        existing_customer = cur.fetchone()

        cur.close()
        conn.close()

        if existing_customer:
            session['customer'] = existing_customer
            return redirect(url_for('accounts', initial=True))
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


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user=os.environ["DB_USERNAME"],
            password=os.environ["DB_PASSWORD"]
        )

        cur = conn.cursor()

        cur.execute('SELECT customerId FROM customers WHERE email = %s', (session['customer'][3],))
        customer_id = cur.fetchone()[0]

        cur.execute('insert into accounts (accountname, customerid)'
                    ' values (%s, %s)',
                    (request.form['accountName'], customer_id),
                    )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('create_account'))

    return render_template('create_account.html')


@app.route('/transaction', methods=['GET', 'POST'])
def add_transaction():
    # Verbindung zur Datenbank herstellen
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    cur.execute('SELECT accountid, accountname FROM accounts WHERE customerid = %s', (session['customer'][0],))
    accounts_data = cur.fetchall()
    cur.execute('SELECT categoryid, category FROM categories WHERE customerid = %s', (session['customer'][0],))
    categories = cur.fetchall()
    cur.execute(
        'SELECT keyword, categoryid FROM keywords WHERE categoryid IN (SELECT categoryid FROM categories WHERE customerid = %s)',
        (session['customer'][0],))
    gross = cur.fetchall()
    print(gross)
    if not accounts_data:
        error = "Bitte neues Konto hinzufügen."
        return render_template('create_account.html', error=error)

    if request.method == 'POST':
        # Benutzerdaten aus dem Formular abrufen
        account_id = request.form.get('accountSelect')
        amount = request.form.get('amount')
        recipient = request.form.get('recipient')
        description = request.form.get('description')
        category = request.form.get('categorySelect')

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        amount = amount.replace(',', '.')
        # Transaktion in die Datenbank einfügen
        if category:
            cur.execute('INSERT INTO transactions (accountid, timestamp, amount, recipient, description, categoryid)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (account_id, timestamp, amount, recipient, description, category))
        else:
            cur.execute('INSERT INTO transactions (accountid, timestamp, amount, recipient, description)'
                        'VALUES (%s, %s, %s, %s, %s)',
                        (account_id, timestamp, amount, recipient, description))
        # Verbindung schließen und Änderungen speichern
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('add_transaction'))

    # Verbindung zur Datenbank herstellen, um Konten abzurufen
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    # Konten aus der Datenbank abrufen
    cur.execute('SELECT accountid, accountname FROM accounts WHERE customerid = %s', (session['customer'][0],))
    accounts_data = cur.fetchall()

    # Verbindung schließen
    cur.close()
    conn.close()

    return render_template('transaction.html', accounts=accounts_data, categories=categories)


@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    initial = request.args.get('initial', False)
    # Verbindung zur Datenbank herstellen, um Konten abzurufen
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    # Konten aus der Datenbank abrufen
    cur.execute('SELECT accountid, accountname FROM accounts WHERE customerid = %s',(session['customer'][0],))
    accounts_data = cur.fetchall()

    if not accounts_data:
        error = "Bitte neues Konto hinzufügen."
        return render_template('create_account.html', error=error)

    cur.execute(
        "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') AS formatted_timestamp, "
        "transactions.amount, transactions.recipient, transactions.description "
        "FROM accounts, transactions "
        "WHERE accounts.customerid = %s AND accounts.accountid = transactions.accountid "
        "ORDER BY transactions.timestamp DESC LIMIT %s",
        (session['customer'][0], 15))

    transactions = cur.fetchall()
    # Verbindung schließen
    cur.close()
    conn.close()

    return render_template('accounts.html', accounts=accounts_data, transactions=transactions, initial=initial)


@app.route('/update_table', methods=['GET'])
def update_table():
    limit = request.args.get('limit', 15)  # Standardwert von 15, wenn keine Grenze angegeben ist
    account_id = request.args.get('account_id', None)

    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    if limit == "all":
        limit_clause = ""
    else:
        limit_clause = f"LIMIT {int(limit)}"

    if account_id and account_id != 'null':
        cur.execute(
            f"SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description "
            "FROM accounts, transactions "
            "WHERE accounts.customerid = %s AND accounts.accountid = transactions.accountid "
            f"AND accounts.accountid = %s "
            "ORDER BY transactions.timestamp DESC "
            f"{limit_clause}",
            (session['customer'][0], int(account_id)))
    else:
        cur.execute(
            "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description "
            "FROM accounts, transactions "
            "WHERE accounts.customerid = %s AND accounts.accountid = transactions.accountid "
            "ORDER BY transactions.timestamp DESC "
            f"{limit_clause}",
            (session['customer'][0],))

    transactions = cur.fetchall()

    # Verbindung schließen
    cur.close()
    conn.close()

    return render_template('table_fragment.html', transactions=transactions)


@app.route('/categories', methods=['GET', 'POST'])
def category_page():
    error_category = ""
    error_keyword= ""
    conn = psycopg2.connect(
        host='localhost',
        database='postgres',
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )
    cur = conn.cursor()

    cur.execute('SELECT categoryid, category FROM categories WHERE customerid = %s', (session['customer'][0],))
    categories = cur.fetchall()

    if request.method == 'POST':
        category = request.form.get('category')
        category_id = request.form.get('categorySelect')
        keyword = request.form.get('keyword')
        if category is not None and all(category != existing_category for _, existing_category in categories):
            cur.execute('INSERT INTO categories (category, customerid)'
                        'VALUES (%s, %s)',
                        (category, session['customer'][0]))
        else:
            error_category = f"{category} ist bereits in der Kategorienliste enthalten."
        if keyword is not None:
            cur.execute('INSERT INTO keywords(keyword, categoryid)'
                        'VALUES (%s, %s)',
                        (keyword, category_id))
        else:
            error_keyword = f"{keyword} ist bereits in der Schlagwortliste enthalten."
        conn.commit()

    cur.close()
    conn.close()

    return render_template('categories.html', categories=categories, errorCategory=error_category,
                           error_keyword=error_keyword)
