import psycopg2
import os


conn = psycopg2.connect(  # establishes connection to database
    host="localhost",
    database="postgres",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"])

cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS customers' 
            '(customerId SERIAL PRIMARY KEY,'
            'firstName VARCHAR(50),'
            'lastName VARCHAR(100),'
            'email VARCHAR(100),'
            'password VARCHAR(100),'
            'age INTEGER,'
            'bankingInstitution VARCHAR(100));'
            )

cur.execute('CREATE TABLE IF NOT EXISTS accounts'
            '(accountId SERIAL PRIMARY KEY,'
            'accountName VARCHAR(30),'
            'customerId INTEGER,'
            'FOREIGN KEY (customerId) REFERENCES customers(customerId));'
            )

cur.execute('CREATE TABLE IF NOT EXISTS transactions'
            '(transactionId SERIAL PRIMARY KEY,'
            'timestamp TIMESTAMP NOT NULL,'
            'amount DECIMAL(10, 2) NOT NULL,'
            'recipient VARCHAR(30) NOT NULL,'
            'description VARCHAR(100),'
            'accountId INTEGER NOT NULL,'
            'FOREIGN KEY (accountId) REFERENCES accounts(accountId));'
            )

conn.commit()

cur.close()
conn.close()
