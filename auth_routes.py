from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

# ================= LOGIN =================
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    # ✅ FIX 1: Role-based redirect if already logged in
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')

            # ✅ FIX 2: Role-based redirect after login
            if user.role == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('user.dashboard'))

        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')

    return render_template('auth/login.html')


# ================= REGISTER =================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        hashed_pw = bcrypt.generate_password_hash(
            request.form['password']
        ).decode('utf-8')

        # ✅ FIX 3: Explicitly set role = 'user'
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_pw,
            role='user'
        )

        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ================= LOGOUT =================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
