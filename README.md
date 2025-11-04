# 📚 Library Management System (CustomTkinter + MySQL)

A modern **Library Management System (LMS)** built with **Python**, **CustomTkinter GUI**, and **MySQL database**.  
This desktop application allows administrators and students to manage books, issue and return them, and track borrowing history — all through a professional and interactive graphical interface.

---

## 🚀 Features

### 👨‍💼 Admin Features
- **Login as Admin** (default credentials below)
- **Register new students**
- **Add, view, search, and delete books**
- **View registered students**
- **View borrowing history (issue/return records)**
- **Dark/Light Mode toggle**

### 🎓 Student Features
- **Login using student credentials**
- **View available books**
- **Search books by title or author**
- **Issue and return books using title and author**
- **View status of books in real time**

---

## 🧩 Technologies Used

| Component | Technology |
|------------|-------------|
| **Programming Language** | Python 3.x |
| **GUI Framework** | CustomTkinter |
| **Database** | MySQL |
| **Hashing** | SHA-256 (for secure password storage) |
| **Theme** | Light/Dark mode support |

---

## 🗄️ Database Details

Database Name: **`library_gui_db`**

### Tables Created:
1. **`users`**
   - Stores admin and student login info  
   - Columns: `id`, `username`, `password_hash`, `role`, `name`

2. **`books`**
   - Stores book details  
   - Columns: `id`, `title`, `author`, `status`, `issued_to`, `issued_on`

3. **`borrow_history`**
   - Tracks book issue and return activities  
   - Columns: `id`, `book_title`, `book_author`, `student_name`, `issued_on`, `returned_on`

---

## ⚙️ Installation & Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/library-management-system.git
cd library-management-system

