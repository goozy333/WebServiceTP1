from flask import Flask
from config import Config
from models import db
from routes.books import books_bp
from routes.students import students_bp
from routes.borrows import borrows_bp
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

app.register_blueprint(books_bp)
app.register_blueprint(students_bp)
app.register_blueprint(borrows_bp)

@app.route('/')
def index():
    return {
        "message": "Welcome to the Flask Book Library API",
        "endpoints": {
            "books": "/books",
            "students": "/students",
            "borrows": "/borrows"
        }
    }

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')