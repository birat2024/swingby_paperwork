import mysql.connector
import os
import dotenv

mytrialdb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd=os.getenv('DB_CONNECTION_STRING'),
)