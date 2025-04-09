from flask import Blueprint, request, jsonify
from models import db, Student
from datetime import datetime

students_bp = Blueprint('students', __name__)

# 🔹 Récupérer tous les étudiants
@students_bp.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([
        {
            'id': s.id, 
            'email': s.email, 
            'first_name': s.first_name, 
            'last_name': s.last_name, 
            'birth_date': s.birth_date.strftime('%Y-%m-%d') if s.birth_date else None
        }
        for s in students
    ])

# 🔹 Récupérer un étudiant par ID
@students_bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({
        'id': student.id,
        'email': student.email,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'birth_date': student.birth_date.strftime('%Y-%m-%d') if student.birth_date else None
    })

# 🔹 Ajouter un étudiant
@students_bp.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data or 'email' not in data or 'first_name' not in data or 'last_name' not in data:
        return jsonify({'error': 'Invalid data, email, first_name and last_name are required'}), 400

    # Vérifier si l'email existe déjà
    existing_student = Student.query.filter_by(email=data['email']).first()
    if existing_student:
        return jsonify({'error': 'A student with this email already exists'}), 400

    birth_date = None
    if 'birth_date' in data:
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    student = Student(
        email=data['email'], 
        first_name=data['first_name'], 
        last_name=data['last_name'], 
        birth_date=birth_date
    )
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully', 'id': student.id}), 201

# 🔹 Mettre à jour un étudiant
@students_bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'email' in data:
        # Vérifier si le nouvel email existe déjà pour un autre étudiant
        if data['email'] != student.email:
            existing_student = Student.query.filter_by(email=data['email']).first()
            if existing_student:
                return jsonify({'error': 'A student with this email already exists'}), 400
        student.email = data['email']
    
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'birth_date' in data:
        try:
            student.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format, expected YYYY-MM-DD'}), 400

    db.session.commit()
    return jsonify({'message': 'Student updated successfully'})

# 🔹 Supprimer un étudiant
@students_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({'message': 'Student deleted successfully'})