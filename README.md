# 📚 Library Management System (Python + MySQL)

## 📖 Overview
The **Library Management System** is a Python-based application designed to manage library operations efficiently.  
It provides **secure login** for both **Admin** and **Student** users, book management, issuing/returning features, and borrowing history — all connected to a **MySQL database** for reliable data storage.

---

## ✨ Features

### 🔑 Login & Registration
- **Role-based access**: Admin & Student
- **Admin-controlled registration**: Only Admin can register new users (requires admin password)
- **Secure credentials** stored in MySQL

### 📚 Book Management (Admin Only)
- Add new books
- Delete books from the system
- View all available books

### 📖 Book Borrowing
- Issue books to students
- Return books and update stock automatically
- Track due dates

### 📝 Borrowing History
- Maintain a record of all issued/returned books
- View borrowing history by student

---

## 🛠️ Tech Stack
- **Programming Language:** Python 3.x
- **Database:** MySQL
- **Libraries Used:**
  - `mysql-connector-python` – Database connectivity
  - `datetime` – Date handling
  - `os` – File handling for extra logs
  - `getpass` – Secure password entry

---

## 📂 Project Structure

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YourUsername/Library_Management_System.git
cd Library_Management_System

2️⃣ Install dependencies
```bash
git clone https://github.com/YourUsername/Library_Management_System.git
cd Library_Management_System
pip install mysql-connector-python

3️⃣ Setup MySQL Database
sql
CREATE DATABASE library_db;
USE library_db;

-- Create tables for users, books, and transactions
-- (Refer to database.sql file if available)

4️⃣ Run the application
bash
python main.py

👥 User Roles
#Admin

Register users

Manage books (Add, Update, Delete)

View borrowing history

#Student

Login & view available books

Borrow and return books

View own borrowing history
