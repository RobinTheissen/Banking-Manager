import psycopg2
import os


conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user=os.environ["DB_USERNAME"],
    password=os.environ["DB_PASSWORD"]
)

cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS customers' 
            '(customerId SERIAL PRIMARY KEY,'
            'firstName VARCHAR(50),'
            'lastName VARCHAR(50),'
            'email VARCHAR(100),'
            'password VARCHAR(100),'
            'age INTEGER,'
            'bankingInstitution VARCHAR(100));'
            )

cur.execute('CREATE TABLE IF NOT EXISTS categories'
            '(categoryId SERIAL PRIMARY KEY,'
            'category VARCHAR(25),'
            'customerId INTEGER NOT NULL,'
            'FOREIGN KEY (customerId) REFERENCES customers(customerId));'
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
            'recipient VARCHAR(50) NOT NULL,'
            'description VARCHAR(100),'
            'accountId INTEGER NOT NULL,'
            'categoryId INTEGER,'
            'FOREIGN KEY (categoryId) REFERENCES categories(categoryId),'
            'FOREIGN KEY (accountId) REFERENCES accounts(accountId));'
            )

cur.execute('CREATE TABLE IF NOT EXISTS keywords'
            '(keywordId SERIAL PRIMARY KEY,'
            'keyword VARCHAR(25),'
            'categoryId INTEGER NOT NULL,'
            'FOREIGN KEY (categoryId) REFERENCES categories(categoryId));'
            )

conn.commit()

cur.close()
conn.close()
