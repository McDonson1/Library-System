import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------
# Initialize session state
# -------------------------------
if "books" not in st.session_state:
    st.session_state.books = []
if "students" not in st.session_state:
    st.session_state.students = []
if "borrowing_records" not in st.session_state:
    st.session_state.borrowing_records = []

books = st.session_state.books
students = st.session_state.students
borrowing_records = st.session_state.borrowing_records

# -------------------------------
# Core Logic Functions
# -------------------------------
def add_book(title, author, isbn):
    if any(b["ISBN"] == isbn for b in books):
        return "Book with this ISBN already exists."
    books.append({"Title": title, "Author": author, "ISBN": isbn, "Borrowed": False})
    return "Book added."

def remove_book(isbn):
    book = next((b for b in books if b["ISBN"] == isbn), None)
    if book:
        books.remove(book)
        return "Book removed."
    return "Book not found."

def add_student(name, student_id):
    if any(s["Student ID"] == student_id for s in students):
        return "Student ID already exists."
    students.append({"Name": name, "Student ID": student_id})
    return "Student added."

def remove_student(student_id):
    student = next((s for s in students if s["Student ID"] == student_id), None)
    if student:
        students.remove(student)
        return "Student removed."
    return "Student not found."

def borrow_book(student_id, isbn):
    student = next((s for s in students if s["Student ID"] == student_id), None)
    book = next((b for b in books if b["ISBN"] == isbn), None)
    if student and book and not book["Borrowed"]:
        book["Borrowed"] = True
        borrowing_records.append({
            "Student ID": student_id,
            "ISBN": isbn,
            "Borrow Date": datetime.now().strftime("%Y-%m-%d"),
            "Return Date": None
        })
        return "Book borrowed."
    return "Borrow failed. Check ID or book status."

def return_book(student_id, isbn):
    book = next((b for b in books if b["ISBN"] == isbn), None)
    record = next((r for r in borrowing_records if r["Student ID"] == student_id and r["ISBN"] == isbn and r["Return Date"] is None), None)
    if book and record:
        book["Borrowed"] = False
        record["Return Date"] = datetime.now().strftime("%Y-%m-%d")
        borrow_date = datetime.strptime(record["Borrow Date"], "%Y-%m-%d")
        return_date = datetime.strptime(record["Return Date"], "%Y-%m-%d")
        fine = (return_date - borrow_date).days - 14
        return f"Returned. Fine: {fine} days." if fine > 0 else "Returned. No fine."
    return "Return failed."

# -------------------------------
# Streamlit Interface
# -------------------------------
st.title("📚 Library Management System")

menu = st.sidebar.selectbox("Choose Option", [
    "Add Book", "Remove Book", "Add Student", "Remove Student",
    "Borrow Book", "Return Book", "List Books", "Search Books", "Search Students",
    "View Borrowing Records", "Backup Data", "Restore Data"
])

# --- Book Management ---
if menu == "Add Book":
    st.header("Add Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    isbn = st.text_input("ISBN")
    if st.button("Add"):
        st.success(add_book(title, author, isbn))

elif menu == "Remove Book":
    st.header("Remove Book")
    isbn = st.text_input("ISBN")
    if st.button("Remove"):
        st.success(remove_book(isbn))

# --- Student Management ---
elif menu == "Add Student":
    st.header("Add Student")
    name = st.text_input("Name")
    student_id = st.text_input("Student ID")
    if st.button("Add"):
        st.success(add_student(name, student_id))

elif menu == "Remove Student":
    st.header("Remove Student")
    student_id = st.text_input("Student ID")
    if st.button("Remove"):
        st.success(remove_student(student_id))

# --- Borrowing ---
elif menu == "Borrow Book":
    st.header("Borrow Book")
    student_id = st.text_input("Student ID")
    isbn = st.text_input("Book ISBN")
    if st.button("Borrow"):
        st.success(borrow_book(student_id, isbn))

elif menu == "Return Book":
    st.header("Return Book")
    student_id = st.text_input("Student ID")
    isbn = st.text_input("Book ISBN")
    if st.button("Return"):
        st.success(return_book(student_id, isbn))

# --- List Books ---
elif menu == "List Books":
    st.header("All Books")
    st.dataframe(books)

# --- Search ---
elif menu == "Search Books":
    query = st.text_input("Search book by title:")
    results = [b for b in books if query.lower() in b["Title"].lower()]
    st.dataframe(results)

elif menu == "Search Students":
    query = st.text_input("Search student by name:")
    results = [s for s in students if query.lower() in s["Name"].lower()]
    st.dataframe(results)

# --- View Records ---
elif menu == "View Borrowing Records":
    st.header("Borrowing Records")
    st.dataframe(borrowing_records)

# --- Backup ---
elif menu == "Backup Data":
    if st.button("Backup Now"):
        with open("library_data.txt", "w") as f:
            f.write("Books:\n")
            for b in books:
                f.write(f"{b['Title']},{b['Author']},{b['ISBN']},{b['Borrowed']}\n")
            f.write("Students:\n")
            for s in students:
                f.write(f"{s['Name']},{s['Student ID']}\n")
            f.write("Borrowing Records:\n")
            for r in borrowing_records:
                f.write(f"{r['Student ID']},{r['ISBN']},{r['Borrow Date']},{r['Return Date']}\n")
        st.success("Backup saved to library_data.txt")

# --- Restore ---
elif menu == "Restore Data":
    if st.button("Restore from Backup"):
        try:
            books.clear()
            students.clear()
            borrowing_records.clear()
            with open("library_data.txt", "r") as f:
                section = None
                for line in f:
                    line = line.strip()
                    if line == "Books:":
                        section = "books"
                    elif line == "Students:":
                        section = "students"
                    elif line == "Borrowing Records:":
                        section = "records"
                    elif section == "books":
                        title, author, isbn, borrowed = line.split(",")
                        books.append({"Title": title, "Author": author, "ISBN": isbn, "Borrowed": borrowed == "True"})
                    elif section == "students":
                        name, sid = line.split(",")
                        students.append({"Name": name, "Student ID": sid})
                    elif section == "records":
                        sid, isbn, bdate, rdate = line.split(",")
                        borrowing_records.append({
                            "Student ID": sid,
                            "ISBN": isbn,
                            "Borrow Date": bdate,
                            "Return Date": rdate if rdate != "None" else None
                        })
            st.success("Data restored from library_data.txt")
        except Exception as e:
            st.error(f"Failed to restore: {e}")
