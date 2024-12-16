from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime
import os
import binascii
from flask_cors import CORS

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)
app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24)).decode()  # Securely generate a secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Archana@localhost:5432/Archons'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the database models
class Customer(db.Model):
    __tablename__ = 'customer'
    serial_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(10), nullable=False)  # Note: Use hashing for passwords in production!

class Record(db.Model):
    __tablename__ = 'records'
    record_id = db.Column(db.Integer, primary_key=True)
    serial_id = db.Column(db.Integer, db.ForeignKey('customer.serial_id', ondelete='CASCADE'), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    total = db.Column(db.Numeric(15, 2))

class Budget(db.Model):
    __tablename__ = 'budgets'
    budget_id = db.Column(db.Integer, primary_key=True)
    serial_id = db.Column(db.Integer, db.ForeignKey('customer.serial_id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    limit = db.Column(db.Numeric(15, 2), nullable=False)
    spent = db.Column(db.Numeric(15, 2), default=0)
    remaining = db.Column(db.Numeric(15,2))

    # Foreign key relationship with the Customer model
    customer = db.relationship("Customer", backref=db.backref("budgets", cascade="all, delete-orphan"))

# Create the database
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('budget.html')

@app.route('/entry')
def hom():
    return render_template('entry.html')

@app.route('/analysis')
def ho():
    return render_template('analysis.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    #if 'serial_id' not in session:
    #    return jsonify({"message": "User not logged in"}), 401
    
    #serial_id = session['serial_id']  # Get serial_id from session
    data = request.get_json()
    serial_id = data['serial_id']
    amount = Decimal(data['amount'])  # Convert amount to Decimal
    transaction_type = data['transaction_type']
    category = data['category']

    # Calculate current total balance (income - expense) for this serial_id
    income_total = db.session.query(func.sum(Record.amount)).filter_by(serial_id=serial_id, transaction_type='Income').scalar() or Decimal('0')
    expense_total = db.session.query(func.sum(Record.amount)).filter_by(serial_id=serial_id, transaction_type='Expense').scalar() or Decimal('0')
    current_balance = income_total - expense_total

    # Get current date in "Fri, 01 Nov 2024" format
    transaction_date = datetime.now().strftime('%a, %d %b %Y')

    # Adjust balance based on the new transaction
    if transaction_type == 'Income':
        current_balance += amount
    elif transaction_type == 'Expense':
        current_balance -= amount
        # Update spent amount in the budget
        budget = Budget.query.filter_by(serial_id=serial_id, category=category).first()
        if budget:
            budget.spent += amount
            db.session.commit()

    # Create the new transaction record
    new_transaction = Record(
        serial_id=serial_id,
        transaction_date= transaction_date,
        transaction_type=transaction_type,
        category=data['category'],
        amount=amount,
        total=current_balance  # Store the calculated total balance here
    )
    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({
        "message": "Transaction added successfully",
        "transaction": {
            "record_id": new_transaction.record_id,
            "serial_id": new_transaction.serial_id,
            "transaction_date": new_transaction.transaction_date,
            "transaction_type": new_transaction.transaction_type,
            "category": new_transaction.category,
            "amount": new_transaction.amount,
            "total": new_transaction.total  # Confirm the updated total balance
        }
    })


@app.route('/get_transaction/<int:serial_id>', methods=['GET'])
def get_transactions(serial_id):
    user = Customer.query.filter_by(serial_id=serial_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    records = Record.query.filter_by(serial_id=user.serial_id).all()
    output = []
    for record in records:
        record_data = {
            'record_id': record.record_id,
            'transaction_date': record.transaction_date.strftime('%a, %d %b %Y'),
            'transaction_type': record.transaction_type,
            'category': record.category,
            'amount': f"{record.amount:.2f}",
            'total': f"{record.total:.2f}" if record.total else None
        }
        output.append(record_data)
    return jsonify(output)

@app.route('/income_category_analysis/<int:serial_id>', methods=['GET'])
def income_category_analysis(serial_id):
    # Query income transactions grouped by category
    income_summary = db.session.query(
        Record.category,
        func.sum(Record.amount).label('total_amount')
    ).filter(
        Record.serial_id == serial_id,
        Record.transaction_type == 'Income'
    ).group_by(Record.category).all()

    # Format the output as a list of dictionaries
    output = [{'category': category, 'total_amount': float(total)} for category, total in income_summary]
    
    return jsonify(output)

@app.route('/expense_category_analysis/<int:serial_id>', methods=['GET'])
def expense_category_analysis(serial_id):
    # Query expense transactions grouped by category
    expense_summary = db.session.query(
        Record.category,
        func.sum(Record.amount).label('total_amount')
    ).filter(
        Record.serial_id == serial_id,
        Record.transaction_type == 'Expense'
    ).group_by(Record.category).all()

    # Format the output as a list of dictionaries
    output = [{'category': category, 'total_amount': float(total)} for category, total in expense_summary]
    
    return jsonify(output)

@app.route('/income_vs_expense_analysis/<int:serial_id>', methods=['GET'])
def income_vs_expense_analysis(serial_id):
    # Calculate total income
    total_income = db.session.query(
        func.sum(Record.amount)
    ).filter(
        Record.serial_id == serial_id,
        Record.transaction_type == 'Income'
    ).scalar() or 0

    # Calculate total expense
    total_expense = db.session.query(
        func.sum(Record.amount)
    ).filter(
        Record.serial_id == serial_id,
        Record.transaction_type == 'Expense'
    ).scalar() or 0

    # Prepare the output
    output = {
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net_balance': float(total_income - total_expense)
    }

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
