from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message

from app import db, mail
from app.models import Complaint
from app.ai_engine.predictor import predict_complaint

user = Blueprint('user', __name__, url_prefix='/user')


# ================= USER ACCESS CHECK =================
def user_only():
    if current_user.role != 'user':
        flash("Unauthorized access!", "danger")
        return False
    return True


# ================= DASHBOARD =================
@user.route('/dashboard')
@login_required
def dashboard():
    if not user_only():
        return redirect(url_for('auth.login'))

    complaints = Complaint.query.filter_by(
        user_id=current_user.id
    ).order_by(Complaint.created_at.desc()).all()

    return render_template(
        'user/dashboard.html',
        complaints=complaints
    )


# ================= CREATE COMPLAINT =================
@user.route('/create', methods=['GET', 'POST'])
@login_required
def create_complaint():
    if not user_only():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        # 🤖 AI Prediction with Error Handling
        # This prevents the app from crashing if the .pkl files are missing or broken
        try:
            category, issue, priority, confidence = predict_complaint(description)
        except Exception as e:
            # Fallback values if the AI Engine fails
            category = "General Banking"
            priority = "Medium"
            confidence = 0.0
            print(f"❌ AI Prediction Error: {e}")

        # Save complaint to the database
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            priority=priority,
            author=current_user
        )

        db.session.add(complaint)
        db.session.commit()

        # ================= EMAIL TO USER =================
        try:
            user_msg = Message(
                subject="✅ Complaint Registered Successfully",
                recipients=[current_user.email]
            )

            user_msg.body = f"""
Hello {current_user.name},

Your complaint has been registered successfully.

Title: {title}
AI Detected Category: {category}
Priority: {priority}

Our team will review your complaint and update the status soon.

Thank you,
Smart Complaint Management System
"""
            mail.send(user_msg)

            # ================= EMAIL TO ADMIN =================
            admin_msg = Message(
                subject="📢 New Complaint Submitted",
                recipients=["drashtidesai752@gmail.com"]
            )

            admin_msg.body = f"""
New Complaint Submitted

User Email: {current_user.email}
Title: {title}
Category: {category}
Priority: {priority}

Description:
{description}
"""
            mail.send(admin_msg)
            
        except Exception as e:
            # If mail fails (e.g. no internet), don't stop the user experience
            print(f"⚠️ Email could not be sent: {e}")

        flash("Complaint registered successfully! Confirmation email sent.", "success")
        return redirect(url_for('user.dashboard'))

    return render_template('user/create.html')