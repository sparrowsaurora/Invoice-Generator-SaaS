from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    service = db.Column(db.String(200))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default="unpaid")
    date = db.Column(db.String(20))
    company_name = db.Column(db.String(120), nullable=False) 
    items = db.Column(db.Text, nullable=False)  # JSON string
    due_date = db.Column(db.String(50))
    
    # Foreign key field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # One-to-many relationship
    invoices = db.relationship('Invoice', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)