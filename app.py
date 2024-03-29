import hashlib
from datetime import timedelta, datetime

from data.Database.DatabaseManager import DatabaseManager
from data.Handler.TextValidator import TextValidator
from data.Customer import Customer
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=60)  # sets the time for data stored to 60 minutes
app.secret_key = 'geheim'


# Robin Theissen
@app.route('/', methods=['GET', 'POST'])
def index():  # Startseite
    customer_name = ""
    if request.method == 'POST':
        if session == {}:  # Überprüft ob die session leer ist
            return render_template('index.html')
        else:  # Gibt den Namen wieder falls ein user sich ausgeloggt hat
            customer_name = session['customer'][1] + " " + session['customer'][2]
            session.clear()
            return render_template('index.html', customer_name=customer_name)

    else:
        return render_template('index.html', customer_name=customer_name)


# Robin Theissen
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'customer' in session:  # Überprüft ob es einen user in der session gibt
        return render_template('accounts.html',)
    customer = Customer
    customer_id = None
    error = ""
    if request.method == 'POST':  # Bei POST: initialisiert DBManager und führt Überprüfungen zu Mail und Passwort durch
        db_manager = DatabaseManager()
        text_validator = TextValidator()

        # Überprüfe, ob die E-Mail bereits in der Datenbank vorhanden ist
        existing_email_count = db_manager.execute_query('SELECT COUNT(*) FROM customers WHERE email = %s',
                                                        (request.form['email'],)).fetchone()[0]

        if existing_email_count > 0:
            # Die E-Mail ist bereits in der Datenbank vorhanden, zeige eine Fehlermeldung

            error = "Die E-Mail ist bereits registriert. Bitte verwende eine andere E-Mail-Adresse."

        elif not text_validator.password_validation(request.form['password']):
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
                hashlib.sha256(request.form['password'].encode()).hexdigest(),
                request.form['bankinginstitution'] if request.form['bankinginstitution'] else None
            )

            db_manager.execute_query(
                'INSERT INTO customers (firstname, lastname, email, password, age, bankinginstitution)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (customer.fName, customer.lName, customer.email, customer.pw, customer.age,
                 customer.bankingInst))

            customer_id = db_manager.execute_query('SELECT customerid FROM customers WHERE email = %s',
                                                   (customer.email,)).fetchone()[0]

        db_manager.commit_and_close()

        # Wenn ein Fehler auftritt, kehre zur Registrierungsseite mit Fehlermeldung zurück
        if error:
            return render_template("register.html", error=error)
        # Erfolgreich registriert, leite den Benutzer zu einer anderen Seite weiter
        else:
            session['customer'] = [customer_id, customer.fName, customer.lName, customer.email, customer.pw,
                                   customer.age,
                                   customer.bankingInst]
            return redirect(url_for('create_account'))

    return render_template("register.html")


# Robin Theissen
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'customer' in session:  # Überprüft ob es einen user in der session gibt
        return render_template('accounts.html',)

    if request.method == 'POST':  # Bei POST: Vergleicht die eingegebenen Daten mit der Datenbank & loggt ein falls
        # passend
        login_email = request.form['email']
        login_password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        db_manager = DatabaseManager()

        existing_customer = db_manager.execute_query('SELECT * FROM customers WHERE email = %s AND password = %s',
                                                     (login_email, login_password)).fetchone()

        db_manager.close()

        if existing_customer:
            session['customer'] = existing_customer
            return redirect(url_for('accounts', initial=True))
        else:
            error = 'Bitte überprüfe die eingegebenen Daten'
            return render_template('login.html', error=error)
    return render_template('login.html')


# Robin Theissen
@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    if request.method == 'POST':  # Bei Post: loggt den Benutzer aus
        return render_template('index.html')
    else:
        return render_template('logout.html')


# Marc Kluge
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    if request.method == 'POST':  # Bei POST: Fügt ein Konto in die Datenbank ein
        db_manager = DatabaseManager()

        customer_id = db_manager.execute_query('SELECT customerId FROM customers WHERE email = %s',
                                               (session['customer'][3],)).fetchone()[0]

        db_manager.execute_query('insert into accounts (accountname, customerid)'
                                 ' values (%s, %s)',
                                 (request.form['accountName'], customer_id), )
        db_manager.commit_and_close()

        return redirect(url_for('create_account'))

    return render_template('create_account.html')


# Robin Theissen & Marc Kluge
@app.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    initial = request.args.get('initial', False)
    # Verbindung zur Datenbank herstellen, um Konten abzurufen
    db_manager = DatabaseManager()

    # Konten aus der Datenbank abrufen
    accounts_data = db_manager.execute_query('SELECT accountid, accountname FROM accounts WHERE customerid = %s',
                                             (session['customer'][0],)).fetchall()

    if not accounts_data:  # Falls noch kein Konto für den customer existiert wir dieser weitergeleitet zu Konto anlegen
        db_manager.close()
        error = "Bitte neues Konto hinzufügen."
        return render_template('create_account.html', error=error)

    transactions = db_manager.execute_query(
        "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') AS formatted_timestamp, "
        "transactions.amount, transactions.recipient, transactions.description, categories.category "
        "FROM accounts "
        "JOIN transactions ON accounts.accountid = transactions.accountid "
        "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
        "WHERE accounts.customerid = %s "
        "ORDER BY transactions.timestamp DESC LIMIT %s",
        (session['customer'][0], 15)
    ).fetchall()

    db_manager.close()

    return render_template('accounts.html', accounts=accounts_data, transactions=transactions, initial=initial)


# Marc Kluge
@app.route('/transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    db_manager = DatabaseManager()

    accounts_data = db_manager.execute_query('SELECT accountid, accountname FROM accounts WHERE customerid = %s',
                                             (session['customer'][0],)).fetchall()
    categories = db_manager.execute_query('SELECT categoryid, category FROM categories WHERE customerid = %s',
                                          (session['customer'][0],)).fetchall()

    if not accounts_data:  # Falls noch kein Konto für den customer existiert wir dieser weitergeleitet zu Konto anlegen
        db_manager.close()
        error = "Bitte neues Konto hinzufügen."
        return render_template('create_account.html', error=error)

    if request.method == 'POST':
        # Benutzerdaten aus dem Formular abrufen
        account_id = request.form.get('accountSelect')
        amount = request.form.get('amount')
        recipient = request.form.get('recipient')
        description = request.form.get('description')
        category = request.form.get('categorySelect')

        # Formatiert den Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        recipient_list = recipient.split()
        description_list = description.split()

        text_validator = TextValidator()

        # Überprüfung für recipient
        if text_validator.transaction_regex_validation(recipient):
            db_manager.close()
            error = "Empfänger darf keine Sonderzeichen enthalten."
            # Handle den Fehler, z.B. durch Rückgabe einer Fehlermeldung an den Benutzer
            return render_template('transaction.html', accounts=accounts_data, categories=categories, error=error)

        # Überprüfung für description
        if text_validator.transaction_regex_validation(description):
            db_manager.close()
            error = "Beschreibung darf keine Sonderzeichen enthalten."
            # Handle den Fehler, z.B. durch Rückgabe einer Fehlermeldung an den Benutzer
            return render_template('transaction.html', accounts=accounts_data, categories=categories, error=error)

        amount = amount.replace(',', '.')  # Ersetzt in Zahlen das Komma durch einen Punkt

        keywordlist = db_manager.execute_query('SELECT keyword, keywords.categoryid FROM keywords, categories WHERE '
                                               'keywords.categoryid = categories.categoryid '
                                               'AND (categories.customerid = %s)',
                                               (session['customer'][0],)).fetchall()
        # Überprüft ob ein Schlagwort im Empfänger steht, falls nicht wird der Verwendungszweck überprüft
        if not category:
            result = False
            for text in recipient_list:
                match = next((value for item, value in keywordlist if item == text), None)
                if match:
                    result = match
                    break

            if not result:
                for text in description_list:
                    match = next((value for item, value in keywordlist if item == text), None)
                    if match:
                        result = match
                        break

            if result:
                category = result

        # Transaktion in die Datenbank einfügen
        if category:
            db_manager.execute_query('INSERT INTO transactions '
                                     '(accountid, timestamp, amount, recipient, description, categoryid)'
                                     'VALUES (%s, %s, %s, %s, %s, %s)',
                                     (account_id, timestamp, amount, recipient, description, category))
        else:
            db_manager.execute_query('INSERT INTO transactions (accountid, timestamp, amount, recipient, description)'
                                     'VALUES (%s, %s, %s, %s, %s)',
                                     (account_id, timestamp, amount, recipient, description))
        # Verbindung schließen und Änderungen speichern
        db_manager.commit_and_close()

        return redirect(url_for('add_transaction'))

    # Konten aus der Datenbank abrufen
    accounts_data = db_manager.execute_query('SELECT accountid, accountname FROM accounts WHERE customerid = %s',
                                             (session['customer'][0],)).fetchall()

    # Verbindung schließen
    db_manager.close()

    return render_template('transaction.html', accounts=accounts_data, categories=categories)


# Marc Kluge
@app.route('/categories', methods=['GET', 'POST'])
def category_page():
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    error_category = ""
    error_keyword = ""
    db_manager = DatabaseManager()

    categories = db_manager.execute_query('SELECT categoryid, category FROM categories WHERE customerid = %s',
                                          (session['customer'][0],)).fetchall()

    if request.method == 'POST':  # Bei POST: Schreibt entweder neue Kategorie, oder Schlagwort zu einer Kategorie in
        # die DB
        category = request.form.get('category')
        category_id = request.form.get('categorySelect')
        keyword = request.form.get('keyword')
        if category is not None and all(category != existing_category for _, existing_category in categories):
            db_manager.execute_query('INSERT INTO categories (category, customerid)'
                                     'VALUES (%s, %s)',
                                     (category, session['customer'][0]))
            categories = db_manager.execute_query('SELECT categoryid, category FROM categories WHERE customerid = %s',
                                                  (session['customer'][0],)).fetchall()
            db_manager.commit_and_close()
        else:
            error_category = f"{category} ist bereits in der Kategorienliste enthalten."
        if keyword is not None:
            error_category = ""
            db_manager.execute_query('INSERT INTO keywords(keyword, categoryid)'
                                     'VALUES (%s, %s)',
                                     (keyword, category_id))
            db_manager.commit_and_close()
        else:
            error_keyword = f"{keyword} ist bereits in der Schlagwortliste enthalten."
            db_manager.close()

    return render_template('categories.html', categories=categories, errorCategory=error_category,
                           error_keyword=error_keyword)


# Robin Theissen
@app.route('/update_table', methods=['GET'])
def update_table():  # Verändert die Anzahl der ausgegebenen Transaktionen auf accounts.html
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    limit = request.args.get('limit', 15)  # Standardwert von 15, wenn keine Grenze angegeben ist
    account_id = request.args.get('account_id', None)

    db_manager = DatabaseManager()

    if limit == "all":
        limit_clause = ""
    else:
        limit_clause = f"LIMIT {int(limit)}"

    if account_id and account_id != 'null':
        transactions = db_manager.execute_query(
            "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') "
            "AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description, categories.category "
            "FROM accounts "
            "JOIN transactions ON accounts.accountid = transactions.accountid "
            "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
            "WHERE accounts.customerid = %s AND accounts.accountid = %s "
            "ORDER BY transactions.timestamp DESC "
            f"{limit_clause}",
            (session['customer'][0], int(account_id))
        ).fetchall()
    else:
        transactions = db_manager.execute_query(
            "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') "
            "AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description, categories.category "
            "FROM accounts "
            "JOIN transactions ON accounts.accountid = transactions.accountid "
            "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
            "WHERE accounts.customerid = %s "
            "ORDER BY transactions.timestamp DESC "
            f"{limit_clause}",
            (session['customer'][0],)
        ).fetchall()

    db_manager.close()

    return render_template('table_fragment.html', transactions=transactions)


# Robin Theissen
@app.route('/update_table/search', methods=['POST'])
def update_table_search():  # Verändert die ausgegebenen Transaktionen auf accounts.html anhand der Suchanfragen
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    if request.method == 'POST':

        keyword = request.form['keyword']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        amount = request.form['amount']
        recipient = request.form['recipient']

        # Basiskomponenten der SQL-Abfrage
        base_query = (
            "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') "
            "AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description, categories.category "
            "FROM accounts "
            "JOIN transactions ON accounts.accountid = transactions.accountid "
            "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
            "WHERE accounts.customerid = %s "
        )

        # Zusätzliche Bedingungen
        where_conditions = []
        params = [session['customer'][0]]

        if keyword:
            where_conditions.append("AND transactions.description ILIKE %s")
            params.append(f"%{keyword}%")

        if start_date:
            where_conditions.append("AND transactions.timestamp >= %s")
            params.append(start_date)

        if end_date:
            where_conditions.append("AND transactions.timestamp <= %s")
            params.append(end_date + " 23:59:59")

        if amount:
            where_conditions.append("AND transactions.amount = %s")
            params.append(amount)

        if recipient:
            where_conditions.append("AND transactions.recipient ILIKE %s")
            params.append(f"%{recipient}%")

        # Erstelle die vollständige WHERE-Klausel
        where_clause = " ".join(where_conditions) if where_conditions else ""

        # Setze die vollständige SQL-Abfrage zusammen

        sql_query = f"{base_query} {where_clause} ORDER BY transactions.timestamp DESC"

        db_manager = DatabaseManager()

        transactions = db_manager.execute_query(sql_query, params).fetchall()
        total_amount = sum(row[2] for row in transactions)

        db_manager.close()

        return render_template('table_fragment.html', transactions=transactions, total_amount=total_amount)


# Marc KLuge
@app.route('/visual', methods=['GET', 'POST'])
def visual():  # Approute zur visuellen Darstellung von Kontoeinträgen
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    if 'pie_chart_data' in session:
        pie_chart_data = session.pop('pie_chart_data')
    else:
        db_manager = DatabaseManager()
        customer_id = session['customer'][0]
        transactions = db_manager.execute_query(
            "SELECT accounts.accountname, to_char(transactions.timestamp, 'DD.MM.YYYY HH24:MI') "
            "AS formatted_timestamp, "
            "transactions.amount, transactions.recipient, transactions.description, categories.category "
            "FROM accounts "
            "JOIN transactions ON accounts.accountid = transactions.accountid "
            "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
            "WHERE accounts.customerid = %s "
            "ORDER BY transactions.timestamp DESC",
            (customer_id,)
        ).fetchall()

        category_totals = {'keine Kategorie': 0.00}

        for transaction in transactions:
            category = transaction[5] if transaction[5] is not None else 'keine Kategorie'
            amount = float(transaction[2])

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        labels = list(category_totals.keys())
        values = list(category_totals.values())

        pie_chart_data = {'labels': labels, 'values': values}

    return render_template('visual.html', pie_chart_data=pie_chart_data)


# Marc Kluge
@app.route('/update_chart', methods=['POST'])
def update_chart():  # Verändert die angezeigte Chart nach eingabe eines Zeitraums
    if 'customer' not in session:  # Überprüft ob es einen user in der session gibt
        return render_template('index.html',
                               error="Ihre Session ist abgelaufen, bitte loggen Sie sich erneut ein.")
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    db_manager = DatabaseManager()

    base_query = ("SELECT accounts.accountname, to_char(transactions.timestamp,"
                  " 'DD.MM.YYYY HH24:MI') AS formatted_timestamp, "
                  "transactions.amount, transactions.recipient, transactions.description, categories.category "
                  "FROM accounts "
                  "JOIN transactions ON accounts.accountid = transactions.accountid "
                  "LEFT JOIN categories ON categories.categoryid = transactions.categoryid "
                  "WHERE accounts.customerid = %s ")

    where_conditions = []
    params = [session['customer'][0]]

    if start_date:
        where_conditions.append("AND transactions.timestamp >= %s")
        params.append(start_date)

    if end_date:
        where_conditions.append("AND transactions.timestamp <= %s")
        params.append(end_date + " 23:59:59")

    # Erstelle die vollständige WHERE-Klausel
    where_clause = " ".join(where_conditions) if where_conditions else ""

    # Setze die vollständige SQL-Abfrage zusammen
    sql_query = f"{base_query} {where_clause} ORDER BY transactions.timestamp DESC"

    # Änderungen in der SQL-Abfrage, um Einträge zwischen start_date und end_date zu erhalten
    transactions = db_manager.execute_query(sql_query, params).fetchall()

    category_totals = {'keine Kategorie': 0.00}

    for transaction in transactions:
        category = transaction[5] if transaction[5] is not None else 'keine Kategorie'
        amount = float(transaction[2])

        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    pie_chart_data = {'labels': labels, 'values': values}

    # Setze die aktualisierten Daten in der Session, damit sie auf der Seite verfügbar sind
    session['pie_chart_data'] = pie_chart_data

    # Führe einen Redirect auf die visual-Seite durch
    return redirect(url_for('visual', pie_chart_data=pie_chart_data))
