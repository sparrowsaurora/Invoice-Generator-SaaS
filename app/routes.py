from flask import Blueprint, render_template, request, redirect, url_for, send_file
from .models import Invoice
from . import db
from weasyprint import HTML
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

        return redirect(url_for('main.index'))
    return render_template('create_invoice.html')

@main.route('/download/<int:id>')
def download_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    html = render_template('invoice_pdf.html', invoice=invoice)
    pdf_file = f"invoice_{invoice.id}.pdf"
    HTML(string=html).write_pdf(pdf_file)
    return send_file(pdf_file, as_attachment=True)
