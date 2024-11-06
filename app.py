from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import mysql.connector
import os
from cryptography.fernet import Fernet

load_dotenv()

app = Flask(__name__)
cipher_suite = Fernet(os.getenv('encryptionKey').encode())


def get_db_connection():
    """Establishes and returns a new database connection."""
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
    )


@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT service_name, username, password FROM passwords")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    decrypted_rows = [
        (service, username, cipher_suite.decrypt(password).decode()) for service, username, password in rows
    ]
    return render_template('index.html', passwords=decrypted_rows)


@app.route('/add', methods=['POST'])
def add_password():
    db = get_db_connection()
    cursor = db.cursor()
    service_name = request.form['service_name']
    username = request.form['username']
    password = cipher_suite.encrypt(request.form['password'].encode())
    
    cursor.execute(
        "INSERT INTO passwords (service_name, username, password) VALUES (%s, %s, %s)",
        (service_name, username, password)
    )
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
def view_passwords():
    db, cursor = get_db_connection()
    cursor.execute("SELECT * FROM passwords")
    rows = cursor.fetchall()
    for row in rows:
        service_name = row[1]
        username = row[2]
        encrypted_password = row[3]
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode() 
        print(f"Service: {service_name}, Username: {username}, Password: {decrypted_password}")
    cursor.close()
    db.close()

def update_password(service_name, new_password):
    db, cursor = get_db_connection()
    encrypted_password = cipher_suite.encrypt(new_password.encode())
    query = "UPDATE passwords SET password = %s WHERE service_name = %s"
    cursor.execute(query, (encrypted_password, service_name))
    db.commit()
    cursor.close()
    db.close()
    print(f"Password for {service_name} updated.")

def delete_password(service_name):
    db, cursor = get_db_connection()
    query = "DELETE FROM passwords WHERE service_name = %s"
    cursor.execute(query, (service_name,))
    db.commit()
    cursor.close()
    db.close()
    print(f"Password for {service_name} deleted.")

if __name__ == "__main__":
    while True:
        print("\nPassword Manager")
        print("1. Add new password")
        print("2. View passwords")
        print("3. Update password")
        print("4. Delete password")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            service = input("Enter service name: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            add_password(service, username, password)
        elif choice == '2':
            view_passwords()
        elif choice == '3':
            service = input("Enter service name to update: ")
            new_password = input("Enter new password: ")
            update_password(service, new_password)
        elif choice == '4':
            service = input("Enter service name to delete: ")
            delete_password(service)
        elif choice == '5':
            break
        else:
            print("Invalid option, please try again.")

    print("Exiting password manager.")

