import threading


class Database:
    """Thread-safe in-memory database store for Enterprise Smart Library."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        self.users = {}
        self.books = {}
        self.loans = []
        self._seed_initial_data()

    def _seed_initial_data(self):
        # Seed default test users
        self.users["U101"] = {
            "user_id": "U101",
            "name": "Alice Johnson",
            "email": "alice@university.edu",
            "role": "Student",
            "active_loans": 0
        }

        self.users["U102"] = {
            "user_id": "U102",
            "name": "Dr. Robert Smith",
            "email": "robert.smith@university.edu",
            "role": "Faculty",
            "active_loans": 0
        }

        # Seed default book catalog
        self.books["B001"] = {
            "book_id": "B001",
            "title": "Cloud Native DevOps Architecture",
            "author": "Linus Torvalds",
            "isbn": "978-0134685991",
            "total_copies": 5,
            "available_copies": 5
        }

        self.books["B002"] = {
            "book_id": "B002",
            "title": "Continuous Delivery Principles",
            "author": "Jez Humble & David Farley",
            "isbn": "978-0321601919",
            "total_copies": 3,
            "available_copies": 3
        }

    def reset(self):
        """Helper to restore state during unit testing teardowns."""
        with self._lock:
            self.users.clear()
            self.books.clear()
            self.loans.clear()
            self._seed_initial_data()


db = Database()
