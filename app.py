from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()


db = mysql.connector.connect(
    host = os.getenv('host'),  
    user = os.getenv('user'),  
    password = os.getenv('password'), 
    database = os.getenv('database')
)

print(db)
