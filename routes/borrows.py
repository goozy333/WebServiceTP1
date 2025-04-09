from flask import Blueprint, request, jsonify
from models import db, Book, Student, StudentBook
from datetime import datetime

borrows_bp = Blueprint('borrows', __name__)

# 🔹 Emprunter un livre
@borrows_bp.route('/borrows', methods=['POST'])
def borrow_book():
    data = request.get_json()

    if not data or 'student_id' not in data or 'book_id' not in data:
        return jsonify({'error': 'Invalid data, student_id and book_id are required'}), 400

    # Vérifier si l'étudiant existe
    student = Student.query.get(data['student_id'])
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Vérifier si le livre existe
    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    # Vérifier si le livre est déjà emprunté par cet étudiant et non rendu
    existing_borrow = StudentBook.query.filter_by(
        student_id=data['student_id'], 
        book_id=data['book_id'],
        return_date=None
    ).first()
    
    if existing_borrow:
        return jsonify({'error': 'This book is already borrowed by this student'}), 400

    # Créer un nouvel emprunt
    borrow_date = datetime.now()
    borrow = StudentBook(
        student_id=data['student_id'],
        book_id=data['book_id'],
        borrow_date=borrow_date,
        return_date=None
    )
    
    db.session.add(borrow)
    db.session.commit()
    
    return jsonify({
        'message': 'Book borrowed successfully',
        'id': borrow.id,
        'borrow_date': borrow_date.strftime('%Y-%m-%d %H:%M:%S')
    }), 201

# 🔹 Retourner un livre
@borrows_bp.route('/borrows/return', methods=['POST'])
def return_book():
    data = request.get_json()

    if not data or 'student_id' not in data or 'book_id' not in data:
        return jsonify({'error': 'Invalid data, student_id and book_id are required'}), 400

    # Trouver l'emprunt actif
    borrow = StudentBook.query.filter_by(
        student_id=data['student_id'],
        book_id=data['book_id'],
        return_date=None
    ).first()
    
    if not borrow:
        return jsonify({'error': 'No active borrow found for this student and book'}), 404

    # Mettre à jour la date de retour
    borrow.return_date = datetime.now()
    db.session.commit()
    
    return jsonify({
        'message': 'Book returned successfully',
        'return_date': borrow.return_date.strftime('%Y-%m-%d %H:%M:%S')
    })

# 🔹 Obtenir tous les emprunts
@borrows_bp.route('/borrows', methods=['GET'])
def get_all_borrows():
    borrows = StudentBook.query.all()
    
    return jsonify([
        {
            'id': b.id,
            'student_id': b.student_id,
            'book_id': b.book_id,
            'borrow_date': b.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': b.return_date.strftime('%Y-%m-%d %H:%M:%S') if b.return_date else None,
            'is_returned': b.return_date is not None
        }
        for b in borrows
    ])

# 🔹 Obtenir les emprunts d'un étudiant
@borrows_bp.route('/students/<int:student_id>/borrows', methods=['GET'])
def get_student_borrows(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
        
    borrows = StudentBook.query.filter_by(student_id=student_id).all()
    
    return jsonify([
        {
            'id': b.id,
            'book_id': b.book_id,
            'borrow_date': b.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': b.return_date.strftime('%Y-%m-%d %H:%M:%S') if b.return_date else None,
            'is_returned': b.return_date is not None
        }
        for b in borrows
    ])

# 🔹 Obtenir l'historique des emprunts d'un livre
@borrows_bp.route('/books/<int:book_id>/borrows', methods=['GET'])
def get_book_borrows(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
        
    borrows = StudentBook.query.filter_by(book_id=book_id).all()
    
    return jsonify([
        {
            'id': b.id,
            'student_id': b.student_id,
            'borrow_date': b.borrow_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': b.return_date.strftime('%Y-%m-%d %H:%M:%S') if b.return_date else None,
            'is_returned': b.return_date is not None
        }
        for b in borrows
    ])