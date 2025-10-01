import struct, os, sys
from datetime import datetime

# --------- Struct definitions ----------
BOOK_STRUCT = struct.Struct("i50s30siiii")    # book_id, title, author, year, copies, borrowed, status
MEMBER_STRUCT = struct.Struct("i40s40s15sii") # member_id, name, email, phone, status, total_borrows
LOAN_STRUCT = struct.Struct("iii10s10s10si")  # borrow_id, book_id, member_id, loan_date, due_date, return_date, status

BOOK_FILE = "books.dat"
MEMBER_FILE = "members.dat"
LOAN_FILE = "loans.dat"

# ---------- helpers for pack/unpack strings ----------
def pack_str(s: str, length: int) -> bytes:
    return s.encode("utf-8")[:length].ljust(length, b"\x00")

def unpack_str(b: bytes) -> str:
    return b.decode("utf-8", errors="ignore").rstrip("\x00")

# ---------- Book pack/unpack ----------
def pack_book(d):
    return BOOK_STRUCT.pack(
        int(d["book_id"]),
        pack_str(d.get("title",""),50),
        pack_str(d.get("author",""),30),
        int(d.get("year",0)),
        int(d.get("copies",0)),
        int(d.get("borrowed",0)),
        int(d.get("status",1))
    )

def unpack_book(raw):
    r = BOOK_STRUCT.unpack(raw)
    return {
        "book_id": r[0],
        "title": unpack_str(r[1]),
        "author": unpack_str(r[2]),
        "year": r[3],
        "copies": r[4],
        "borrowed": r[5],
        "status": r[6]
    }

# ---------- Member pack/unpack ----------
def pack_member(d):
    return MEMBER_STRUCT.pack(
        int(d["member_id"]),
        pack_str(d.get("name",""),40),
        pack_str(d.get("email",""),40),
        pack_str(d.get("phone",""),15),
        int(d.get("status",1)),
        int(d.get("total_borrows",0))
    )

def unpack_member(raw):
    r = MEMBER_STRUCT.unpack(raw)
    return {
        "member_id": r[0],
        "name": unpack_str(r[1]),
        "email": unpack_str(r[2]),
        "phone": unpack_str(r[3]),
        "status": r[4],
        "total_borrows": r[5]
    }

# ---------- Loan pack/unpack ----------
def pack_loan(d):
    return LOAN_STRUCT.pack(
        int(d["borrow_id"]),
        int(d["book_id"]),
        int(d["member_id"]),
        pack_str(d.get("loan_date",""),10),
        pack_str(d.get("due_date",""),10),
        pack_str(d.get("return_date",""),10),
        int(d.get("status",0))
    )

def unpack_loan(raw):
    r = LOAN_STRUCT.unpack(raw)
    return {
        "borrow_id": r[0],
        "book_id": r[1],
        "member_id": r[2],
        "loan_date": unpack_str(r[3]),
        "due_date": unpack_str(r[4]),
        "return_date": unpack_str(r[5]),
        "status": r[6]   # 0 = Borrowed (active), 1 = Return
    }

# ---------- Storage helpers ----------
def read_all(filename, size):
    if not os.path.exists(filename):
        return []
    items = []
    with open(filename,"rb") as f:
        while True:
            chunk = f.read(size)
            if not chunk or len(chunk) < size:
                break
            items.append(chunk)
    return items

# Books
def load_books():
    chunks = read_all(BOOK_FILE, BOOK_STRUCT.size)
    return [unpack_book(c) for c in chunks]

def save_books(list_books):
    with open(BOOK_FILE,"wb") as f:
        for b in list_books:
            f.write(pack_book(b))

def append_book_record(b):
    with open(BOOK_FILE,"ab") as f:
        f.write(pack_book(b))

# Members
def load_members():
    chunks = read_all(MEMBER_FILE, MEMBER_STRUCT.size)
    return [unpack_member(c) for c in chunks]

def save_members(list_members):
    with open(MEMBER_FILE,"wb") as f:
        for m in list_members:
            f.write(pack_member(m))

def append_member_record(m):
    with open(MEMBER_FILE,"ab") as f:
        f.write(pack_member(m))

# Loans
def load_loans():
    chunks = read_all(LOAN_FILE, LOAN_STRUCT.size)
    return [unpack_loan(c) for c in chunks]

def save_loans(list_loans):
    with open(LOAN_FILE,"wb") as f:
        for l in list_loans:
            f.write(pack_loan(l))

def append_loan_record(l):
    with open(LOAN_FILE,"ab") as f:
        f.write(pack_loan(l))

# ---------- Utility ----------
def next_id(items, key):
    if not items:
        return 1
    return max(i[key] for i in items) + 1

def input_int(prompt, default=None):
    while True:
        s = input(prompt).strip()
        if s == "" and default is not None:
            return default
        try:
            return int(s)
        except:
            print("Please enter a valid number.")

def input_str(prompt, default=""):
    s = input(prompt)
    return s if s != "" else default

def today():
    return datetime.now().strftime("%Y-%m-%d")

# ---------- CRUD: Books ----------
def add_book():
    books = load_books()
    count = input_int("How many books do you want to add? ", default=1)

    for idx in range(1, count+1):
        print(f"\n--- Adding book {idx} of {count} ---")
        while True:
            bid = input_int("Book ID: ")
            if any(b["book_id"] == bid for b in books):
                print("This Book ID already exists. Please enter a different ID.")
            else:
                break

        title = input_str("Title: ")
        author = input_str("Author: ")
        year = input_int("Year: ", default=0)
        copies = input_int("Copies: ", default=1)

        b = {
            "book_id": bid,
            "title": title,
            "author": author,
            "year": year,
            "copies": copies,
            "borrowed": 0,
            "status": 1
        }
        append_book_record(b)
        books.append(b)
        print(f"Book added successfully.")

def view_books():
    books = load_books()
    if not books:
        print("No books.")
        return

    header_fmt = "{:<6} | {:<30} | {:<20} | {:<4} | {:<6} | {:<8}"
    row_fmt    = header_fmt

    print()
    print(header_fmt.format("ID","Title","Author","Year","Copies","Status"))
    print("-"*90)

    for b in books:
        status = "Active" if b['status']==1 else "Inactive"
        print(row_fmt.format(
            b['book_id'],
            b['title'][:30],
            b['author'][:20],
            b['year'],
            b['copies'],
            status
        ))

    print("-"*90)

def update_book():
    books = load_books()
    bid = input_int("Enter book_id to update: ")
    found = False
    for i,b in enumerate(books):
        if b["book_id"] == bid:
            found = True
            print("Leave blank to keep current.")
            title = input_str(f"Title [{b['title']}] : ", default=b['title'])
            author = input_str(f"Author [{b['author']}] : ", default=b['author'])
            year = input_int(f"Year [{b['year']}] : ", default=b['year'])
            copies = input_int(f"Copies [{b['copies']}] : ", default=b['copies'])
            b["title"]=title; b["author"]=author; b["year"]=year; b["copies"]=copies
            books[i]=b
            break
    if found:
        save_books(books)
        print("Book updated.")
    else:
        print("Not found.")

def delete_book():
    books = load_books()
    loans = load_loans()
    bid = input_int("Enter book_id to delete: ")

    active_loans = [l for l in loans if l["book_id"] == bid and l["status"] == 0]
    if active_loans:
        print("Cannot delete this book. It is currently borrowed by someone.")
        return

    found = False
    for i, b in enumerate(books):
        if b["book_id"] == bid:
            if b["status"] == 0:
                print("This book has already been deleted (Inactive). Cannot delete again.")
                return
            b["status"] = 0   # mark inactive
            books[i] = b
            found = True
            break

    if found:
        save_books(books)
        print("Book deleted (status set to Inactive).")
    else:
        print("Not found.")

# ---------- CRUD: Members ----------
def add_member():
    members = load_members()
    count = input_int("How many members do you want to add? ", default=1)

    for idx in range(1, count+1):
        print(f"\n--- Adding member {idx} of {count} ---")
        mid = next_id(members, "member_id")
        name = input_str("Name: ")
        email = input_str("Email: ")
        phone = input_str("Phone: ")

        m = {
            "member_id": mid,
            "name": name,
            "email": email,
            "phone": phone,
            "status": 1,
            "total_borrows": 0
        }
        append_member_record(m)
        members.append(m)
        print(f"Added member id {mid}")


def view_members():
    members = load_members()
    if not members:
        print("No members.")
        return

    header_fmt = "{:<8} | {:<30} | {:<30} | {:<12} | {:<8} | {:<12}"
    row_fmt    = header_fmt

    print()
    print(header_fmt.format("MemberID","Name","Email","Phone","Status","TotalBorrows"))
    print("-"*113)

    for m in members:
        status = "Active" if m["status"]==1 else "Blocked"
        print(row_fmt.format(
            m['member_id'], m['name'][:30], m['email'][:30],
            m['phone'], status, m['total_borrows']
        ))
    print("-"*113)


def update_member():
    members = load_members()
    mid = input_int("Enter member_id to update: ")
    found=False
    for i,m in enumerate(members):
        if m["member_id"]==mid:
            found=True
            name = input_str(f"Name [{m['name']}] : ", default=m['name'])
            email = input_str(f"Email [{m['email']}] : ", default=m['email'])
            phone = input_str(f"Phone [{m['phone']}] : ", default=m['phone'])
            m['name']=name; m['email']=email; m['phone']=phone
            members[i]=m
            break
    if found:
        save_members(members)
        print("Member updated.")
    else:
        print("Not found.")

def delete_member():
    members = load_members()
    mid = input_int("Member ID to delete: ")
    found=False
    for i,m in enumerate(members):
        if m["member_id"]==mid:
            m["status"]=0
            members[i]=m
            found=True
            break
    if found:
        save_members(members)
        print("Member deleted.")
    else:
        print("Not found.")

# ---------- Borrow / Return ----------
def borrow_book():
    books = load_books()
    members = load_members()
    loans = load_loans()
    book_id = input_int("Book ID to borrow: ")
    member_id = input_int("Member ID: ")
    book = next((b for b in books if b["book_id"]==book_id and b["status"]==1), None)
    member = next((m for m in members if m["member_id"]==member_id and m["status"]==1), None)
    if not book:
        print("Book not available.")
        return
    if not member:
        print("Member not valid.")
        return
    if book["borrowed"] >= book["copies"]:
        print("No available copies.")
        return
    borrow_id = next_id(loans, "borrow_id")
    loan_date = today()
    due_date = input_str("Due date (YYYY-MM-DD): ", default="")
    loan = {
        "borrow_id": borrow_id,
        "book_id": book_id,
        "member_id": member_id,
        "loan_date": loan_date,
        "due_date": due_date,
        "return_date": "",
        "status": 0  # 0 = Borrowed
    }
    append_loan_record(loan)
    # update book
    for i,b in enumerate(books):
        if b["book_id"]==book_id:
            b["borrowed"] += 1
            books[i]=b
            break
    save_books(books)
    # update member total borrows
    for i,m in enumerate(members):
        if m["member_id"]==member_id:
            m["total_borrows"] += 1
            members[i]=m
            break
    save_members(members)
    print("Borrow recorded. " \
    "")

def return_book():
    loans = load_loans()
    books = load_books()
    members = load_members()
    borrow_id = input_int("Borrow ID to return: ")
    found=False
    for i,l in enumerate(loans):
        if l["borrow_id"]==borrow_id and l["status"]==0:
            found=True
            l["return_date"] = today()
            l["status"] = 1  # returned
            loans[i]=l
            # update book borrowed
            for j,b in enumerate(books):
                if b["book_id"]==l["book_id"]:
                    b["borrowed"] = max(0, b["borrowed"] - 1)
                    books[j]=b
                    break
            break
    if found:
        save_loans(loans)
        save_books(books)
        print("Return success.")
    else:
        print("Active loan not found.")

def view_loans():
    loans = load_loans()
    books = load_books()
    members = load_members()

    if not loans:
        print("No loans.")
        return

    book_map = {b["book_id"]: b["title"] for b in books}
    member_map = {m["member_id"]: m["name"] for m in members}

    header_fmt = "{:<8} | {:<6} | {:<30} | {:<8} | {:<25} | {:<10} | {:<10} | {:<10} | {:<10}"
    row_fmt    = header_fmt

    print()
    print(header_fmt.format(
        "BorrowID", "BookID", "BookTitle", "MemberID", "MemberName",
        "LoanDate", "DueDate", "ReturnDate", "Status"
    ))
    print("-"*140)

    for l in loans:
        status = "Borrowed" if l["status"]==0 else "Returned"
        book_title = book_map.get(l["book_id"], f"Book{l['book_id']}")
        member_name = member_map.get(l["member_id"], f"Member{l['member_id']}")

        print(row_fmt.format(
            l['borrow_id'],
            l['book_id'], book_title[:30],
            l['member_id'], member_name[:25],
            l['loan_date'], l['due_date'], l['return_date'], status
        ))

    print("-"*140)

# ---------- Report (display on screen, no file) ----------
def show_summary_report():
    books = load_books()
    members = load_members()
    loans = load_loans()
    member_map = {m["member_id"]: m["name"] for m in members}

    total_titles = 0
    total_copies = 0
    total_borrowed_now = 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("\n" + "="*137)
    print("LIBRARY SUMMARY REPORT".center(135))
    print(f"Generated : {now}".center(135))
    print("="*137)

    header_fmt = "{:<6} | {:<30} | {:<20} | {:<4} | {:<6} | {:<8} | {:<25} | {:<8} | {:<5}"
    row_fmt    = header_fmt

    print(header_fmt.format("ID","Title","Author","Year","Copies","Borrowed","Borrowers","Status","Avail"))
    print("-"*137)

    for b in books:
        if b["status"] != 1:
            continue
        total_titles += 1
        total_copies += b["copies"]

        active_loans = [ln for ln in loans if ln["book_id"]==b["book_id"] and ln["status"]==0]
        borrower_names = [member_map.get(ln["member_id"], f"Member{ln['member_id']}") for ln in active_loans]
        borrowers_display = ", ".join(borrower_names) if borrower_names else "-"

        borrowed_count = b["borrowed"]
        total_borrowed_now += borrowed_count
        avail = b["copies"] - borrowed_count
        status = "Active" if b["status"]==1 else "Inactive"

        print(row_fmt.format(
            b['book_id'], b['title'][:30], b['author'][:20], b['year'],
            b['copies'], borrowed_count, borrowers_display[:25], status, avail
        ))

    print("-"*137)
    print("INVENTORY SUMMARY")
    print(f"- Total Titles   : {total_titles}")
    print(f"- Total Copies   : {total_copies}")
    print(f"- Borrowed Now   : {total_borrowed_now}")
    print(f"- Available Now  : {total_copies - total_borrowed_now}")
    print("="*137)
    print("END OF REPORT".center(135))
    print("="*137 + "\n")

# ---------- Menus ----------
def books_menu():
    while True:
        print("\n--- Books Menu ---")
        print("1. Add Book")
        print("2. View Books")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. Back")
        c = input("Choose: ").strip()
        if c=="1": add_book()
        elif c=="2": view_books()
        elif c=="3": update_book()
        elif c=="4": delete_book()
        elif c=="5": break
        else: print("Invalid")

def members_menu():
    while True:
        print("\n--- Members Menu ---")
        print("1. Add Member")
        print("2. View Members")
        print("3. Update Member")
        print("4. Delete Member")
        print("5. Back")
        c = input("Choose: ").strip()
        if c=="1": add_member()
        elif c=="2": view_members()
        elif c=="3": update_member()
        elif c=="4": delete_member()
        elif c=="5": break
        else: print("Invalid")

def loans_menu():
    while True:
        print("\n--- Borrow/Return Menu ---")
        print("1. Borrow Book")
        print("2. Return Book")
        print("3. View Loans")
        print("4. Back")
        c = input("Choose: ").strip()
        if c=="1": borrow_book()
        elif c=="2": return_book()
        elif c=="3": view_loans()
        elif c=="4": break
        else: print("Invalid")

def main_menu():
    while True:
        print("\n=== Library System ===")
        print("1. Manage Books")
        print("2. Manage Members")
        print("3. Borrow/Return")
        print("4. Reports")
        print("5. Exit")
        c = input("Choose: ").strip()
        if c=="1": books_menu()
        elif c=="2": members_menu()
        elif c=="3": loans_menu()
        elif c=="4": show_summary_report()
        elif c=="5":
            print("Bye.")
            sys.exit(0)
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main_menu()