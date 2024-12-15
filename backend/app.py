from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import psycopg2
import bcrypt
from statement import read_and_concat_tables 
import pandas as pd
from dotenv import load_dotenv
import os
from bot import FinanceChatbotModel 
import requests

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "supersecretkey"  # For flashing messages

# Ensure 'uploads' folder exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Your News API key
NEWS_API_KEY = '2d81a14081ae4493892bbcf8a2526c47'


# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the chatbot model with your API key
chatbot = FinanceChatbotModel(api_key)

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
    return render_template('budget_planner.html')  # Render your budget planner page

@app.route('/articles')
def articles():
    return render_template('articles.html')  # Render your articles page

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')  # Render your chatbot page


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


if __name__ == '__main__':
    app.run(debug=True)
