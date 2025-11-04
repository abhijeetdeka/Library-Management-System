"""
Library Management System with CustomTkinter + MySQL
----------------------------------------------------
Features:
- Admin login (default admin: username=admin, password=admin123)
- Admin can register new students
- Students can issue, return, search, and view books
- Admin can view borrowing history of all students
- Uses MySQL database: library_gui_db
- Admin removes book using Title & Author
- Students issue/return book using Title & Author
"""

import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib
import datetime
import sys
import traceback

# ------------------- DB CONFIG -------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "manjeetdeka@123"   # <-- Change this if needed
DB_NAME = "library_gui_db"


# ------------------- HELPER FUNCTIONS -------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )


# ------------------- INIT DATABASE -------------------
def init_database():
    # Create database if not exists
    conn = None
    try:
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, autocommit=True)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.close()
        conn.close()
    except Exception as e:
        print("Failed creating database:", e)
        if conn:
            conn.close()
        raise

    # Create required tables
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            password_hash VARCHAR(128),
            role ENUM('admin','student') DEFAULT 'student',
            name VARCHAR(100)
        )
        """)

        # Books table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            author VARCHAR(255),
            status VARCHAR(20) DEFAULT 'Available',
            issued_to VARCHAR(100),
            issued_on DATE
        )
        """)

        # Borrow history table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS borrow_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_title VARCHAR(255),
            book_author VARCHAR(255),
            student_name VARCHAR(100),
            issued_on DATE,
            returned_on DATE
        )
        """)

        # Create default admin if not exists
        admin_username = "admin"
        admin_password = "admin123"
        cur.execute("SELECT id FROM users WHERE username=%s AND role='admin'", (admin_username,))
        existing_admin = cur.fetchone()

        if not existing_admin:
            cur.execute(
                "INSERT INTO users (name, username, password_hash, role) VALUES (%s, %s, %s, 'admin')",
                ("Administrator", admin_username, hash_password(admin_password))
            )
            # Avoid messagebox here (no root yet). Print so init never fails.
            print("Default admin created: username=admin password=admin123")
        else:
            print("Admin account already exists.")

        conn.commit()
    finally:
        cur.close()
        conn.close()


# ------------------- MAIN APP -------------------
class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(" Library Management System")
        self.geometry("1000x600")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.current_user = None
        self.login_screen()

    # ---------- LOGIN SCREEN ----------
    def login_screen(self):
        self.clear_window()
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(padx=50, pady=50, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Library Management System", font=("Helvetica", 24, "bold")).pack(pady=20)
        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)
        ctk.CTkButton(frame, text="Login", command=self.authenticate).pack(pady=15)
        ctk.CTkSwitch(frame, text="Dark Mode", command=self.toggle_theme).pack(pady=5)

    def toggle_theme(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("Light" if mode == "Dark" else "Dark")

    def authenticate(self):
        username, password = self.username_entry.get().strip(), self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id,password_hash,role,name FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
        except Exception as e:
            messagebox.showerror("DB Error", f"Database error during login:\n{e}")
            return
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        if user and hash_password(password) == user[1]:
            self.current_user = {"id": user[0], "username": username, "role": user[2], "name": user[3]}
            if user[2] == "admin":
                self.admin_dashboard()
            else:
                self.student_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    # ---------- ADMIN DASHBOARD ----------
    def admin_dashboard(self):
        self.clear_window()
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text=f"Admin: {self.current_user['username']}", font=("Helvetica", 14, "bold")).pack(pady=20)

        buttons = [
            ("Register Student", self.register_student_screen),
            ("View Students", self.view_students_screen),
            ("Add Book", self.add_book_screen),
            ("View Books", self.view_books_screen),
            ("Search Books", self.search_book_screen),
            ("Delete Book", self.delete_book_screen),
            ("View Borrow History", self.view_borrow_history_screen)
        ]
        for name, func in buttons:
            ctk.CTkButton(sidebar, text=name, command=func).pack(pady=6, padx=12, fill="x")

        ctk.CTkButton(sidebar, text="Logout", fg_color="#D9534F", hover_color="#C9302C",
                      command=self.login_screen).pack(side="bottom", pady=20, padx=12, fill="x")

        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)
        self.show_welcome("Admin")

    # ---------- STUDENT DASHBOARD ----------
    def student_dashboard(self):
        self.clear_window()
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text=f"Student: {self.current_user['name']}", font=("Helvetica", 14, "bold")).pack(pady=20)

        buttons = [
            ("View Books", self.view_books_screen),
            ("Search Books", self.search_book_screen),
            ("Issue Book", self.issue_book_screen),
            ("Return Book", self.return_book_screen)
        ]
        for name, func in buttons:
            ctk.CTkButton(sidebar, text=name, command=func).pack(pady=6, padx=12, fill="x")

        ctk.CTkButton(sidebar, text="Logout", fg_color="#D9534F", hover_color="#C9302C",
                      command=self.login_screen).pack(side="bottom", pady=20, padx=12, fill="x")

        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)
        self.show_welcome("Student")

    def show_welcome(self, role):
        # ensure main_frame exists
        try:
            self.clear_main()
        except Exception:
            pass
        ctk.CTkLabel(self.main_frame, text=f"Welcome {role} Dashboard", font=("Helvetica", 20, "bold")).pack(pady=20)

    # ---------- REGISTER STUDENT ----------
    def register_student_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Register New Student", font=("Helvetica", 18, "bold")).pack(pady=15)
        name_e = ctk.CTkEntry(self.main_frame, placeholder_text="Full Name"); name_e.pack(pady=5, fill="x")
        user_e = ctk.CTkEntry(self.main_frame, placeholder_text="Username"); user_e.pack(pady=5, fill="x")
        pass_e = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*"); pass_e.pack(pady=5, fill="x")

        def register():
            n, u, p = name_e.get().strip(), user_e.get().strip(), pass_e.get()
            if not n or not u or not p:
                messagebox.showwarning("Input Error", "All fields are required.")
                return
            conn = None
            cur = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO users (name,username,password_hash,role) VALUES (%s,%s,%s,'student')",
                            (n, u, hash_password(p)))
                conn.commit()
                messagebox.showinfo("Success", "Student registered successfully.")
                name_e.delete(0, "end"); user_e.delete(0, "end"); pass_e.delete(0, "end")
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Username already exists or invalid.\n{err}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        ctk.CTkButton(self.main_frame, text="Register Student", command=register).pack(pady=10)

    # ---------- ISSUE BOOK ----------
    def issue_book_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Issue Book (by Title & Author)", font=("Helvetica", 18, "bold")).pack(pady=10)
        t = ctk.CTkEntry(self.main_frame, placeholder_text="Book Title"); t.pack(pady=5, fill="x")
        a = ctk.CTkEntry(self.main_frame, placeholder_text="Author Name"); a.pack(pady=5, fill="x")

        def issue():
            title, author = t.get().strip(), a.get().strip()
            if not title or not author:
                messagebox.showwarning("Input Error", "Both fields required.")
                return
            conn = None
            cur = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT id,status FROM books WHERE title=%s AND author=%s", (title, author))
                book = cur.fetchone()
                if not book:
                    messagebox.showerror("Error", "Book not found.")
                    return
                if book[1] != "Available":
                    messagebox.showwarning("Error", "Book not available.")
                    return
                today = datetime.date.today()
                cur.execute("UPDATE books SET status='Issued', issued_to=%s, issued_on=%s WHERE id=%s",
                            (self.current_user["name"], today, book[0]))
                # Record in history
                cur.execute("INSERT INTO borrow_history (book_title, book_author, student_name, issued_on) VALUES (%s,%s,%s,%s)",
                            (title, author, self.current_user["name"], today))
                conn.commit()
                messagebox.showinfo("Success", "Book issued successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to issue book:\n{e}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        ctk.CTkButton(self.main_frame, text="Issue", command=issue).pack(pady=10)

    # ---------- RETURN BOOK ----------
    def return_book_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Return Book (by Title & Author)", font=("Helvetica", 18, "bold")).pack(pady=10)
        t = ctk.CTkEntry(self.main_frame, placeholder_text="Book Title"); t.pack(pady=5, fill="x")
        a = ctk.CTkEntry(self.main_frame, placeholder_text="Author Name"); a.pack(pady=5, fill="x")

        def ret():
            title, author = t.get().strip(), a.get().strip()
            if not title or not author:
                messagebox.showwarning("Input Error", "Both fields required.")
                return
            conn = None
            cur = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("UPDATE books SET status='Available', issued_to=NULL, issued_on=NULL WHERE title=%s AND author=%s AND issued_to=%s",
                            (title, author, self.current_user["name"]))
                conn.commit()
                if cur.rowcount > 0:
                    # Update history returned date
                    cur.execute("""
                        UPDATE borrow_history SET returned_on=%s 
                        WHERE book_title=%s AND book_author=%s AND student_name=%s AND returned_on IS NULL
                        ORDER BY id DESC LIMIT 1
                    """, (datetime.date.today(), title, author, self.current_user["name"]))
                    conn.commit()
                    messagebox.showinfo("Success", "Book returned successfully.")
                else:
                    messagebox.showwarning("Error", "No matching issued book found.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to return book:\n{e}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        ctk.CTkButton(self.main_frame, text="Return", command=ret).pack(pady=10)

    # ---------- VIEW BORROW HISTORY ----------
    def view_borrow_history_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Borrowing History", font=("Helvetica", 18, "bold")).pack(pady=10)
        box = ctk.CTkTextbox(self.main_frame, width=900, height=400)
        box.pack(padx=10, pady=10, fill="both", expand=True)

        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT student_name, book_title, book_author, issued_on, returned_on FROM borrow_history ORDER BY id DESC")
            rows = cur.fetchall()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch borrow history:\n{e}")
            return
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        box.insert("end", f"{'Student':<20}{'Title':<30}{'Author':<25}{'Issued On':<15}{'Returned On':<15}\n")
        box.insert("end", "-" * 110 + "\n")
        for r in rows:
            box.insert("end", f"{(r[0] or ''):<20}{(r[1] or ''):<30}{(r[2] or ''):<25}{str(r[3] or ''):<15}{str(r[4] or ''):<15}\n")
        box.configure(state="disabled")

    # ---------- DELETE BOOK ----------
    def delete_book_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Delete Book (by Title & Author)", font=("Helvetica", 18, "bold")).pack(pady=10)
        t = ctk.CTkEntry(self.main_frame, placeholder_text="Book Title"); t.pack(pady=5, fill="x")
        a = ctk.CTkEntry(self.main_frame, placeholder_text="Author Name"); a.pack(pady=5, fill="x")

        def delete():
            title, author = t.get().strip(), a.get().strip()
            if not title or not author:
                messagebox.showwarning("Input Error", "Please enter both title and author.")
                return
            conn = None
            cur = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM books WHERE title=%s AND author=%s", (title, author))
                conn.commit()
                if cur.rowcount > 0:
                    messagebox.showinfo("Deleted", "Book deleted successfully.")
                else:
                    messagebox.showinfo("Not Found", "No book found with that title and author.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete book:\n{e}")
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

        ctk.CTkButton(self.main_frame, text="Delete", command=delete).pack(pady=10)

    # ---------- VIEW BOOKS ----------
    def view_books_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Books", font=("Helvetica", 18, "bold")).pack(pady=10)
        box = ctk.CTkTextbox(self.main_frame, width=900, height=400)
        box.pack(padx=10, pady=10, fill="both", expand=True)
        conn = None
        cur = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id,title,author,status,issued_to FROM books")
            rows = cur.fetchall()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to fetch books:\n{e}")
            return
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

        box.insert("end", f"{'ID':<5}{'Title':<35}{'Author':<25}{'Status':<12}{'Issued To':<20}\n")
        box.insert("end", "-"*100 + "\n")
        for r in rows:
            box.insert("end", f"{r[0]:<5}{(r[1] or ''):<35}{(r[2] or ''):<25}{(r[3] or ''):<12}{str(r[4] or ''):<20}\n")
        box.configure(state="disabled")

    # ---------- SEARCH BOOK ----------
    def search_book_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Search Book", font=("Helvetica", 18, "bold")).pack(pady=10)
        e = ctk.CTkEntry(self.main_frame, placeholder_text="Title or Author"); e.pack(pady=5, fill="x")
        box = ctk.CTkTextbox(self.main_frame, width=900, height=300); box.pack(padx=10, pady=10, fill="both", expand=True)

        def search():
            query = e.get().strip()
            if not query:
                messagebox.showwarning("Input Error", "Please enter a book title or author name.")
                return
            like_query = "%" + query + "%"
            conn = None
            cur = None
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT id,title,author,status,issued_to FROM books WHERE title LIKE %s OR author LIKE %s", (like_query, like_query))
                rows = cur.fetchall()
            except Exception as ex:
                messagebox.showerror("DB Error", f"Search failed:\n{ex}")
                return
            finally:
                if cur:
                    cur.close()
                if conn:
                    conn.close()

            box.configure(state="normal")
            box.delete("0.0", "end")
            if not rows:
                messagebox.showinfo("Not Found", f"No matches found for '{query}'.")
            else:
                box.insert("end", f"{'ID':<5}{'Title':<35}{'Author':<25}{'Status':<12}{'Issued To':<20}\n")
                box.insert("end", "-"*100 + "\n")
                for r in rows:
                    box.insert("end", f"{r[0]:<5}{(r[1] or ''):<35}{(r[2] or ''):<25}{(r[3] or ''):<12}{str(r[4] or ''):<20}\n")
            box.configure(state="disabled")

        ctk.CTkButton(self.main_frame, text="Search", command=search).pack(pady=5)

    # ---------- CLEAR FUNCTIONS ----------
    def clear_window(self):
        for w in self.winfo_children():
            w.destroy()

    def clear_main(self):
        # safe clear when main_frame exists
        if hasattr(self, "main_frame") and self.main_frame is not None:
            for w in self.main_frame.winfo_children():
                w.destroy()
                   
    # ---------- ADD BOOK ----------
    def add_book_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Add New Book", font=("Helvetica", 18, "bold")).pack(pady=15)

        title_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Book Title")
        title_entry.pack(pady=5, fill="x")
        author_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Author Name")
        author_entry.pack(pady=5, fill="x")

        def add_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            if not title or not author:
                messagebox.showwarning("Input Error", "Both fields are required.")
                return
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO books (title, author, status) VALUES (%s, %s, 'Available')", (title, author))
                conn.commit()
                messagebox.showinfo("Success", "Book added successfully.")
                title_entry.delete(0, "end")
                author_entry.delete(0, "end")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
            finally:
                cur.close()
                conn.close()

        ctk.CTkButton(self.main_frame, text="Add Book", command=add_book).pack(pady=10)

    # ---------- VIEW STUDENTS ----------
    def view_students_screen(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Registered Students", font=("Helvetica", 18, "bold")).pack(pady=10)

        box = ctk.CTkTextbox(self.main_frame, width=900, height=400)
        box.pack(padx=10, pady=10, fill="both", expand=True)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, username FROM users WHERE role='student'")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        box.insert("end", f"{'ID':<5}{'Name':<30}{'Username':<25}\n")
        box.insert("end", "-" * 60 + "\n")
        for r in rows:
            box.insert("end", f"{r[0]:<5}{r[1]:<30}{r[2]:<25}\n")
        box.configure(state="disabled")


# ------------------- RUN APP -------------------
if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        # If DB init fails, show an error and exit
        tb = traceback.format_exc()
        print("Database initialization failed:\n", tb)
        messagebox.showerror("Database Error", f"Error initializing database:\n{e}")
        sys.exit(1)

    app = LibraryApp()
    app.mainloop()
    


