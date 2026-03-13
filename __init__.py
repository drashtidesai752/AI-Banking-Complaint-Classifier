from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Gmail SMTP Configuration (CORRECT)
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME='drashtidesai752@gmail.com',
        MAIL_PASSWORD='tdcxxeozgiuevikz',  # ❗ NO SPACES
        MAIL_DEFAULT_SENDER='drashtidesai752@gmail.com'
    )

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.user import user
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user)
    app.register_blueprint(admin_bp)

    return app
