from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from .models import Invoice
from . import db
from xhtml2pdf import pisa
import io
from datetime import datetime, timezone
import os
from flask_login import login_required, current_user
import json


main = Blueprint('main', __name__)

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.landing'))
    
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.date.desc()).all()
    total_invoices = len(invoices)
    total_revenue = sum(inv.amount for inv in invoices)
    last_invoice_date = invoices[0].date if invoices else "N/A"
    recent_invoices = invoices[:5]

    return render_template(
        'index.html',
        total_invoices=total_invoices,
        total_revenue=total_revenue,
        last_invoice_date=last_invoice_date,
        recent_invoices=recent_invoices
    )

@main.route('/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == "POST":
        try:
            client_name = request.form["client_name"]
            company_name = request.form["company_name"]
            service = request.form["service"]
            amount = float(request.form["amount"])
            date = request.form.get("date") or datetime.today().strftime('%Y-%m-%d')
            due_date = request.form.get("due_date") or ""
            items_raw = request.form["items"]

            # Parse and validate items JSON
            items = json.loads(items_raw)

            invoice = Invoice(
                client_name=client_name,
                company_name=company_name,
                service=service,
                amount=amount,
                date=date,
                due_date=due_date,
                items=json.dumps(items),  # Save as JSON string
                user_id=current_user.id
            )

            db.session.add(invoice)
            db.session.commit()
            return redirect(url_for('main.confirm_invoice', id=invoice.id))
        except Exception as e:
            flash(f"Error creating invoice: {e}", "danger")

    return render_template('create_invoice.html')

@main.route('/confirm/<int:id>')
@login_required
def confirm_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    # Decode JSON string into Python list/dict
    items = json.loads(invoice.items)
    return render_template('confirm_invoice.html', invoice=invoice, items=items)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    if request.method == "POST":
        try:
            invoice.client_name = request.form["client_name"]
            invoice.company_name = request.form["company_name"]
            invoice.service = request.form["service"]
            invoice.amount = float(request.form["amount"])
            invoice.date = request.form.get("date") or invoice.date
            invoice.due_date = request.form.get("due_date") or ""
            items_raw = request.form["items"]

            # Validate and update items
            invoice.items = json.dumps(json.loads(items_raw))

            db.session.commit()
            return redirect(url_for('main.confirm_invoice', id=invoice.id))
        except Exception as e:
            flash(f"Error updating invoice: {e}", "danger")

    return render_template('edit_invoice.html', invoice=invoice)

@main.route('/download/<int:id>')
@login_required
def download_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    
    try:
        item_list = json.loads(invoice.items)
    except:
        item_list = []

    html = render_template('invoice_pdf.html', invoice=invoice, items=item_list)

    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), dest=result)

    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'
        return response
    return "PDF generation failed", 500

# @main.route('/send/<int:id>') # Use stmp to send pdf and email template to input user. (maybe list to send to email on database? model for invoiuce)
# @login_required
# def send_invoice(id):
#     # invoice = Invoice.query.get_or_404(id)
#     # # Decode JSON string into Python list/dict
#     # items = json.loads(invoice.items)
#     # return render_template('send_invoice.html', invoice=invoice, items=items)

@main.route('/landing')
def landing():
    return render_template('landing.html')

@main.route('/invoices')
@login_required
def invoices():
    invoices = Invoice.query.filter_by(user_id=current_user.id).order_by(Invoice.date.desc()).all()
    # recent_invoices = invoices[:30]
    return render_template(
        'all_invoices.html',
        invoices=invoices
        # recent_invoices=recent_invoices
    )

@main.route('/account')
@login_required
def account():
    return render_template('account.html', user=current_user)

@main.route('/invoice/<int:id>/archive', methods=['POST'])
@login_required
def archive_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'archived'
    db.session.commit()
    flash('Invoice archived.')
    return redirect(url_for('main.index'))

@main.route('/invoice/<int:id>/unarchive', methods=['POST'])
@login_required
def unarchive_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'unpaid'  # Or 'active' if that’s your logic
    db.session.commit()
    flash('Invoice unarchived.')
    return redirect(url_for('main.index'))