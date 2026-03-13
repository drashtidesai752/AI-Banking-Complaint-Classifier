import os

class Config:
    # Security Key for Sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'corporate_secure_key_2025'
    
    # Database Connection (MySQL)
    # REPLACE '0000' WITH YOUR ACTUAL MYSQL PASSWORD
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@localhost/advanced_complaint_dbsqli'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:0000@localhost/advanced_complaint_dbsqli"

    SQLALCHEMY_TRACK_MODIFICATIONS = False