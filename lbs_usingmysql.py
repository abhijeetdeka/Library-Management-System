import mysql.connector
import datetime
import pwinput

# --- DB Connection ---
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="manjeetdeka@123",  #  Change this
        database="lbs_db"
    )

# --- Authentication ---
def authenticate(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def register_user():
    admin_pwd = pwinput.pwinput("Enter admin password to register new user: ", mask="*")
    if admin_pwd != 'admin123':
        print("Incorrect admin password.")
        return

    username = input("Enter new student's username: ").strip()
    password = pwinput.pwinput("Enter password for the new student: ", mask="*")

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')", (username, password))
        conn.commit()
        print(f"Student '{username}' registered successfully.")
    except mysql.connector.IntegrityError:
        print("Username already exists.")
    conn.close()

def view_registered_students():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE role='student'")
    students = cursor.fetchall()
    conn.close()
    
    print("\n Registered Students:")
    if students:
        for s in students:
            print(f" - {s[0]}")
    else:
        print(" No students found.")
    input("\nPress Enter to return...")

# --- Book Functions ---
def load_books():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM books")
    books = [b[0] for b in cursor.fetchall()]
    conn.close()
    return books

def add_book():
    title = input("Enter book title to add: ").strip()
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO books (title) VALUES (%s)", (title,))
        conn.commit()
        print(f"'{title}' added successfully.")
    except mysql.connector.IntegrityError:
        print(" Book already exists.")
    conn.close()

def remove_book():
    title = input("Enter book title to remove: ").strip()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE title=%s", (title,))
    conn.commit()
    if cursor.rowcount > 0:
        print(f" '{title}' removed.")
    else:
        print(" Book not found.")
    conn.close()

# --- Issue / Return ---
def issue_book(username):
    title = input("Enter book title to issue: ").strip()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE title=%s", (title,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM books WHERE title=%s", (title,))
        cursor.execute("INSERT INTO history (book_title, username, action, date_time) VALUES (%s, %s, 'Issued', %s)", 
                       (title, username, datetime.datetime.now()))
        conn.commit()
        print(f" '{title}' issued to {username}.")
    else:
        print(" Book not available.")
    conn.close()

def return_book(username):
    title = input("Enter book title to return: ").strip()
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO books (title) VALUES (%s)", (title,))
    except mysql.connector.IntegrityError:
        pass  # Book already exists
    cursor.execute("INSERT INTO history (book_title, username, action, date_time) VALUES (%s, %s, 'Returned', %s)",
                   (title, username, datetime.datetime.now()))
    conn.commit()
    conn.close()
    print(f" '{title}' returned by {username}.")

# --- Viewing ---
def view_books():
    books = load_books()
    print("\n Available Books:")
    if books:
        for book in books:
            print(f" - {book}")
    else:
        print(" No books available.")
    input("\nPress Enter to return...")

def view_history():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT book_title, username, action, date_time FROM history ORDER BY date_time DESC")
    records = cursor.fetchall()
    conn.close()

    print("\n Borrowing History:")
    if records:
        for r in records:
            print(f" - {r[2]}: '{r[0]}' by {r[1]} on {r[3]}")
    else:
        print(" No records.")
    input("\nPress Enter to return...")

# --- Dashboards ---
def admin_dashboard():
    while True:
        print("\n=== Admin Dashboard ===")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. View Available Books")
        print("4. View Borrowing History")
        print("5. Register New Student")
        print("6. View Registered Students")
        print("7. Logout")

        choice = input("Enter your choice: ")
        if choice == '1':
            add_book()
        elif choice == '2':
            remove_book()
        elif choice == '3':
            view_books()
        elif choice == '4':
            view_history()
        elif choice == '5':
            register_user()
        elif choice == '6':
            view_registered_students()
        elif choice == '7':
            print(" Logged out.")
            break
        else:
            print(" Invalid choice.")

def student_dashboard(username):
    while True:
        print(f"\n=== Student Dashboard ({username}) ===")
        print("1. Issue Book")
        print("2. Return Book")
        print("3. View Available Books")
        print("4. Logout")

        choice = input("Enter your choice: ")
        if choice == '1':
            issue_book(username)
        elif choice == '2':
            return_book(username)
        elif choice == '3':
            view_books()
        elif choice == '4':
            print(" Logged out.")
            break
        else:
            print(" Invalid choice.")

# --- Login ---
def login():
    print("=== Library Login ===")
    username = input("Username: ").strip()
    password = pwinput.pwinput("Password: ", mask="*")
    role = authenticate(username, password)
    if role == 'admin':
        print(f" Welcome Admin {username}!")
        admin_dashboard()
    elif role == 'student':
        print(f" Welcome {username}!")
        student_dashboard(username)
    else:
        print(" Login failed. Invalid credentials.")

# --- Main Entry ---
def main():
    while True:
        print("\n=== Library Management System ===")
        print("1. Login")
        print("2. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            login()
        elif choice == '2':
            print(" Goodbye!")
            break
        else:
            print(" Invalid choice.")

if __name__ == "__main__":
    main()
    

