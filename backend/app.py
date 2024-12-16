from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
import os
import binascii
import pandas as pd
import joblib
import bcrypt
import psycopg2
import random
import requests
from bot import FinanceChatbotModel 
from statement import read_and_concat_tables

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "supersecretkey"  # For flashing messages
app.config['SECRET_KEY'] = binascii.hexlify(os.urandom(24)).decode()  # Securely generate a secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Archana@localhost:5432/Archons'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# Ensure 'uploads' folder exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Your News API key
NEWS_API_KEY = 'Your api key'


# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the chatbot model with your API key
chatbot = FinanceChatbotModel(api_key)

# Load the trained model
model = joblib.load(r'E:\Finance_management\instance\budget_recommendation_model.pkl')

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

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="Archons",
            user="first_username",
            password="Archana"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Register Route
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed!'}), 500

    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO customer (username, password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 200
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'message': 'Username or email already exists!'}), 400
    finally:
        cur.close()
        conn.close()

# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Database connection failed!'}), 500

    cur = conn.cursor()
    try:
        cur.execute("SELECT password FROM customer WHERE username = %s", (username,))
        result = cur.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid credentials!'}), 400
    finally:
        cur.close()
        conn.close()

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    return render_template('home.html')

@app.route("/statement_analyse")
def statement_analyse():
    return render_template("statement_analyse.html")

@app.route('/budget_planner')
def budget_planner():
    return render_template('budget.html')  # Render your budget planner page

@app.route('/articles')
def articles():
    return render_template('articles.html')  # Render your articles page

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')  # Render your chatbot page

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


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'bank' not in request.form:
        return jsonify({"error": "Must upload a file and select the bank name"}), 400

    file = request.files['file']
    bank_name = request.form['bank']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # Process the file using your existing function
        combined_df, recommend = read_and_concat_tables(file_path, bank_name.lower())
        os.remove(file_path)  # Clean up uploaded file

        recommend_message = recommend['overall_recommendations'][0]
        recommend_df = recommend['monthly_recommendations']

        combined_df = combined_df.applymap(lambda x: str(x) if isinstance(x, pd.Period) else x)
        recommend_df = recommend_df.applymap(lambda x: str(x) if isinstance(x, pd.Period) else x)

        data_json = combined_df.to_dict(orient="records")
        recommend_data = recommend_df.to_dict(orient="records")

        total_credit_values = [
            entry.get('total_credit', 0)
            for entry in recommend_data
            if isinstance(entry.get('total_credit', None), (int, float))
        ]
        average_total_credit = sum(total_credit_values) / len(total_credit_values) if total_credit_values else 0

        return jsonify(
            data=data_json,
            recommend_message=recommend_message,
            recommend_data=recommend_data,
            average_total_credit=average_total_credit
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_articles', methods=['GET'])
def get_articles():
    # API endpoint with your API key
    url = f'https://newsapi.org/v2/everything?q=finance management&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        data = response.json()

        # Check if the response contains articles
        if 'articles' in data:
            articles = data['articles'][:1000]  # Limit to 10 articles
            formatted_articles = [
                {
                    "title": article['title'],
                    "description": article['description'],
                    "url": article['url'],
                    "source": article['source']['name']
                }
                for article in articles
            ]
            return jsonify(formatted_articles), 200
        else:
            return jsonify({"error": "No articles found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chatbot", methods=["POST"])
def chatbot_interaction():
    data = request.get_json()  
    user_message = data.get("message", "")  # Get user input from the JSON

    if not user_message:
        return jsonify({"error": "No message provided"})

    # Get the response from the chatbot
    bot_response = chatbot.get_response(user_message)

    # Return the bot's response as JSON
    return jsonify({"response": bot_response})

# Function to recommend budgets based on remaining total_credit
def recommend_budgets(total_credit):
    categories = ["Food", "Education", "Bills", "Health","Clothing","Savings","Beauty","Entertainment"]
    
    recommendations = []
    
    for category in categories:
        # Calculate spending_ratio and remaining_ratio (mock values for simplicity)
        spending_ratio = random.uniform(0.2, 0.8)  # Example random ratio for spending
        remaining_ratio = 1 - spending_ratio  # Complementary ratio for remaining amount
        
        # Prepare the input for prediction as a DataFrame with correct column names
        input_data = pd.DataFrame([[total_credit, spending_ratio, remaining_ratio]], 
                                  columns=['total_credit', 'spending_ratio', 'remaining_ratio'])
        
        # Predict the budget for this category
        predicted_limit = model.predict(input_data)[0]
        
        # Ensure the predicted limit doesn't exceed the remaining total_credit
        if predicted_limit > total_credit:
            predicted_limit = total_credit
        
        # Add the recommendation for this category
        recommendations.append({
            'category': category,
            'recommended_limit': round(predicted_limit, 2)
        })
        
        # Update the total_credit by subtracting the predicted budget for this category
        total_credit -= predicted_limit
    
    return recommendations

# API endpoint to get budget recommendations
@app.route('/recommend_budgets/<float:total_credit>', methods=['POST'])
def get_recommendations(total_credit):
    #data = request.json
    
    # Get total_credit from the request JSON, default to 5000 if not provided
    #total_credit = data.get('total_credit', 5000)
    
    # Get budget recommendations based on total_credit
    recommendations = recommend_budgets(total_credit)
    
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
