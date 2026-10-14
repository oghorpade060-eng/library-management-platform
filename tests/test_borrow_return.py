
import pytest
from database.db import db
from app.services.library_service import LibraryService


@pytest.fixture(autouse=True)
def run_around_tests():
    db.reset()
    yield
    db.reset()


def test_borrow_and_return_book_lifecycle():
    initial_avail = db.books["B001"]["available_copies"]
    loan = LibraryService.borrow_book("U101", "B001")
    assert loan["status"] == "ACTIVE"
    assert db.books["B001"]["available_copies"] == initial_avail - 1
    assert db.users["U101"]["active_loans"] == 1

    return_record = LibraryService.return_book("U101", "B001")
    assert return_record["status"] == "RETURNED"
    assert db.books["B001"]["available_copies"] == initial_avail
    assert db.users["U101"]["active_loans"] == 0


def test_student_quota_enforcement():
    # Student U101 quota is 3
    LibraryService.add_book("B10", "Book 1", "Auth", "111", 5)
    LibraryService.add_book("B20", "Book 2", "Auth", "222", 5)
    LibraryService.add_book("B30", "Book 3", "Auth", "333", 5)
    LibraryService.add_book("B40", "Book 4", "Auth", "444", 5)
    LibraryService.borrow_book("U101", "B10")
    LibraryService.borrow_book("U101", "B20")
    LibraryService.borrow_book("U101", "B30")

    with pytest.raises(ValueError, match="quota exceeded"):
        LibraryService.borrow_book("U101", "B40")
