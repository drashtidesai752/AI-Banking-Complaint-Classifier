from app import create_app, db
from app.models import User
from app import bcrypt

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="drashtidesai752@gmail.com").first():
            admin = User(
                name="System Admin",
                email="drashtidesai752@gmail.com",
                password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created")

    app.run(debug=True)
