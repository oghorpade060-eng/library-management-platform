
from flask import Blueprint, request, jsonify
from app.services.library_service import LibraryService


api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def healthcheck():
    """Liveness and readiness endpoint for Kubernetes & Docker healthchecks."""
    return jsonify({
        "status": "UP",
        "service": "Enterprise Smart Library Management Platform",
        "version": "1.0.0"
    }), 200


@api_bp.route("/users", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    try:
        user = LibraryService.add_user(
            user_id=data.get("user_id"),
            name=data.get("name"),
            email=data.get("email"),
            role=data.get("role", "Student")
        )
        return jsonify({"message": "User registered successfully", "user": user}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = LibraryService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@api_bp.route("/books", methods=["GET"])
def list_books():
    q = request.args.get("q", "")
    books = LibraryService.search_books(q)
    return jsonify({"count": len(books), "books": books}), 200


@api_bp.route("/books", methods=["POST"])
def add_book():
    data = request.get_json() or {}
    try:
        book = LibraryService.add_book(
            book_id=data.get("book_id"),
            title=data.get("title"),
            author=data.get("author"),
            isbn=data.get("isbn"),
            total_copies=int(data.get("total_copies", 1))
        )
        return jsonify({"message": "Book added successfully", "book": book}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.get_json() or {}
    try:
        loan = LibraryService.borrow_book(
            user_id=data.get("user_id"),
            book_id=data.get("book_id")
        )
        return jsonify({"message": "Book checked out successfully", "loan": loan}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@api_bp.route("/return", methods=["POST"])
def return_book():
    data = request.get_json() or {}
    try:
        loan = LibraryService.return_book(
            user_id=data.get("user_id"),
            book_id=data.get("book_id")
        )
        return jsonify({"message": "Book returned successfully", "loan": loan}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
