from flask import Blueprint, render_template, request, redirect, url_for, send_file, make_response
from .models import Invoice
from . import db
from xhtml2pdf import pisa
import io
import datetime
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    invoices = Invoice.query.all()
    return render_template('index.html', invoices=invoices)

@main.route('/create', methods=['GET', 'POST'])
def create_invoice():
    if request.method == "POST":
        client_name = request.form["client_name"]
        service = request.form["service"]
        amount = float(request.form["amount"])
        date = request.form["date"]
        
        invoice = Invoice(client_name=client_name, service=service, amount=amount, date=date)
        db.session.add(invoice)
        db.session.commit()

        return redirect(url_for('main.confirm_invoice', id=invoice.id))  # New holding page
    return render_template('create_invoice.html')

@main.route('/confirm/<int:id>')
def confirm_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return render_template('confirm_invoice.html', invoice=invoice)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_invoice(id):
    invoice = Invoice.query.get_or_404(id)

    if request.method == "POST":
        invoice.client_name = request.form["client_name"]
        invoice.service = request.form["service"]
        invoice.amount = float(request.form["amount"])
        invoice.date = request.form["date"]

        db.session.commit()
        return redirect(url_for('main.confirm_invoice', id=invoice.id))

    return render_template('edit_invoice.html', invoice=invoice)

@main.route('/download/<int:id>')
def download_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    html = render_template('invoice_pdf.html', invoice=invoice)

    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), dest=result)
    
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{invoice.id}.pdf'
        return response
    return "PDF generation failed", 500

@main.route('/landing')
def landing():
    return render_template('landing.html')