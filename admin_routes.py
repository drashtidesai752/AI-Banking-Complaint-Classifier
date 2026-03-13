from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_mail import Message
from sqlalchemy import case, func

from app import db, mail
from app.models import Complaint

# ================= BLUEPRINT =================
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ================= ADMIN ACCESS CHECK =================
def admin_only():
    if current_user.role != 'admin':
        flash("Unauthorized access!", "danger")
        return False
    return True


# ================= ADMIN DASHBOARD =================
@admin_bp.route('/dashboard')
@login_required
def dashboard():

    if not admin_only():
        return redirect(url_for('auth.login'))

    # 🔍 Filters
    category = request.args.get('category')
    priority = request.args.get('priority')
    status = request.args.get('status')

    query = Complaint.query

    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    if status:
        query = query.filter_by(status=status)

    # 🔥 PRIORITY ORDER (High → Medium → Low)
    priority_order = case(
        (Complaint.priority == 'High', 3),
        (Complaint.priority == 'Medium', 2),
        (Complaint.priority == 'Low', 1),
        else_=0
    )

    complaints = query.order_by(
        priority_order.desc(),
        Complaint.created_at.desc()
    ).all()

   # Optimized Stats
    stats = {
    "total": len(complaints), # Use the list already fetched
    "high": sum(1 for c in complaints if c.priority == 'High'),
    "resolved": sum(1 for c in complaints if c.status == 'Resolved')
}

    return render_template(
        'admin/dashboard.html',
        complaints=complaints,
        stats=stats
    )


# ================= UPDATE STATUS =================
@admin_bp.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):

    if not admin_only():
        return redirect(url_for('auth.login'))

    complaint = Complaint.query.get_or_404(id)
    new_status = request.form.get('status')

    if not new_status:
        flash("Invalid status update", "danger")
        return redirect(url_for('admin.dashboard'))

    complaint.status = new_status
    db.session.commit()

    # 📧 EMAIL TO COMPLAINT OWNER
    msg = Message(
        subject="🔔 Complaint Status Updated",
        recipients=[complaint.author.email]
    )

    msg.body = f"""
Hello {complaint.author.name},

Your complaint status has been updated.

Complaint ID: #{complaint.id}
Title: {complaint.title}
Category: {complaint.category}
Priority: {complaint.priority}

New Status: {new_status}

Thank you,
Smart Complaint Management System
"""

    mail.send(msg)

    flash("Status updated successfully & email sent to user.", "success")
    return redirect(url_for('admin.dashboard'))


# ================= ANALYTICS DASHBOARD =================
@admin_bp.route('/analytics')
@login_required
def analytics():

    if not admin_only():
        return redirect(url_for('auth.login'))

    # 🔹 CATEGORY-WISE DATA
    category_data = db.session.query(
        Complaint.category,
        func.count(Complaint.id)
    ).group_by(Complaint.category).all()
    categories = [c[0] for c in category_data]
    category_counts = [c[1] for c in category_data]

    # 🔹 PRIORITY-WISE DATA
    priority_data = db.session.query(
        Complaint.priority,
        func.count(Complaint.id)
    ).group_by(Complaint.priority).all()
    priorities = [p[0] for p in priority_data]
    priority_counts = [p[1] for p in priority_data]

    return render_template(
        'admin/analytics.html',
        categories=categories,
        category_counts=category_counts,
        priorities=priorities,
        priority_counts=priority_counts
    )
