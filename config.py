from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_LOCATION')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
