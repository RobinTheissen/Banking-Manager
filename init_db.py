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

conn.commit()

cur.close()
conn.close()
