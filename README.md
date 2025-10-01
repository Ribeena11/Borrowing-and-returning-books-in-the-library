# Borrowing and returning books in the library

A command-line based **Borrowing and returning books in the library** written in Python.  
It allows managing books, members, and borrow/return transactions, storing data in binary files (`.dat`).

---

## 📌 Features
- **Books Management**
  - Add, update, delete, and view books
  - Stored fields: `book_id`, `title`, `author`, `year`, `copies`, `borrowed`, `status`
- **Members Management**
  - Add, update, delete, and view members
  - Stored fields: `member_id`, `name`, `email`, `phone`, `status`, `total_borrows`
- **Borrow / Return System**
  - Borrow books and set due dates
  - Return books and update status
  - Stored fields: `borrow_id`, `book_id`, `member_id`, `loan_date`, `due_date`, `return_date`, `status`
- **Reports**
  - Generate summary reports of available books, borrowed books, and active borrowers

---

## ⚙️ File Structure
- `librarySystem.py` — main program
- `books.dat` — binary storage for books
- `members.dat` — binary storage for members
- `loans.dat` — binary storage for loan records

---
