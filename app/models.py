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
