
from database.db import db
from datetime import datetime


class LibraryService:
    """Encapsulates enterprise business rules for the library system."""

    @staticmethod
    def add_user(user_id, name, email, role="Student"):
        if not user_id or not name or not email:
            raise ValueError("All user fields (user_id, name, email) are mandatory.")
        if user_id in db.users:
            raise ValueError(f"User with ID '{user_id}' already exists.")

        user_record = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "active_loans": 0
        }
        db.users[user_id] = user_record
        return user_record

    @staticmethod
    def get_user(user_id):
        return db.users.get(user_id)

    @staticmethod
    def delete_user(user_id):
        user = db.users.get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found.")
        if user["active_loans"] > 0:
            raise ValueError(f"Cannot delete user '{user_id}' with active book loans.")
        del db.users[user_id]
        return True

    @staticmethod
    def add_book(book_id, title, author, isbn, total_copies=1):
        if not book_id or not title or not author or not isbn:
            raise ValueError("All book fields (book_id, title, author, isbn) are mandatory.")
        if book_id in db.books:
            raise ValueError(f"Book with ID '{book_id}' already exists.")
        if total_copies < 1:
            raise ValueError("Total copies must be at least 1.")

        book_record = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "isbn": isbn,
            "total_copies": total_copies,
            "available_copies": total_copies
        }
        db.books[book_id] = book_record
        return book_record

    @staticmethod
    def get_book(book_id):
        return db.books.get(book_id)

    @staticmethod
    def search_books(query=""):
        q = query.lower().strip()
        if not q:
            return list(db.books.values())
        return [
            b for b in db.books.values()
            if q in b["title"].lower() or q in b["author"].lower() or q in b["isbn"].lower()
        ]

    @staticmethod
    def borrow_book(user_id, book_id):
        user = db.users.get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not registered.")
        book = db.books.get(book_id)
        if not book:
            raise ValueError(f"Book '{book_id}' not found in catalog.")

        # Enforce quota: Students can borrow max 3 books
        max_quota = 5 if user["role"] == "Faculty" else 3
        if user["active_loans"] >= max_quota:
            raise ValueError(f"User loan quota exceeded (Max: {max_quota}).")
        if book["available_copies"] <= 0:
            raise ValueError(f"Book '{book['title']}' is currently out of stock.")

        # Update inventory and record loan
        book["available_copies"] -= 1
        user["active_loans"] += 1
        loan_record = {
            "loan_id": f"L-{len(db.loans) + 1:04d}",
            "user_id": user_id,
            "book_id": book_id,
            "borrowed_at": datetime.utcnow().isoformat(),
            "status": "ACTIVE"
        }
        db.loans.append(loan_record)
        return loan_record

    @staticmethod
    def return_book(user_id, book_id):
        user = db.users.get(user_id)
        book = db.books.get(book_id)
        if not user or not book:
            raise ValueError("Invalid user or book ID.")

        active_loan = None
        for loan in db.loans:
            if loan["user_id"] == user_id and loan["book_id"] == book_id and loan["status"] == "ACTIVE":
                active_loan = loan
                break

        if not active_loan:
            raise ValueError(f"No active loan found for user '{user_id}' and book '{book_id}'.")

        active_loan["status"] = "RETURNED"
        active_loan["returned_at"] = datetime.utcnow().isoformat()
        book["available_copies"] += 1
        user["active_loans"] -= 1
        return active_loan
