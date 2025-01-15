# Finance_management
## FinBuild (Team Archons)
A modern, responsive finance management website tailored for students. This project demonstrates best practices in web development using Flask, HTML, CSS, JavaScript, and PostgreSQL.

---

## Table of Contents
1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Screenshots](#screenshots)
6. [Contributors](#contributors)
7. [Contact](#contact)

---

## Features
- **Budget Tracking**: Tracks expenses and budgets effectively.
- **AI-Based Budget Recommendations**: Provides customized budget suggestions based on user needs.
- **Budget Goals & Planning**: Allows students to set financial goals and create strategic plans.
- **Statement Analyzer**: Analyzes financial statements and provide budget recommendations.
- **Articles Section**: Access informative articles on finance management.
- **Chatbot Integration**: Integrated chatbot for answering finance queries.

---

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Styling**: CSS
- **APIs**: News API, Gemini API
- **ML Models**: K-means, Random forest
---

## Installation
### Prerequisites
- Python 3.x
- Install the pakages.
   ```bash
   pip install Flask flask-cors flask-sqlalchemy sqlalchemy python-decouple python-dotenv pandas joblib bcrypt psycopg2 requests

- Create your own API key and add it to .env file.
   1. News API : https://newsapi.org/
   2. Gemini API : https://ai.google.dev/gemini-api/docs
- PostgreSQL installed and running
   
### Steps to Run the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/Archana-K-M/Finance_management.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Finance_management
   ```
3. Set up a virtual environment:(optional if environment is set already)
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database:
   1. Create a database named Archons with password Archana
   2. Create tables using these commands.
      ```bash
      CREATE TABLE customer (
       serial_id SERIAL PRIMARY KEY,
       username VARCHAR(20) UNIQUE NOT NULL,
       password VARCHAR(60) NOT NULL  -- Ensure it's hashed
         );
      ```
      ```bash
      CREATE TABLE records (
       record_id SERIAL PRIMARY KEY,
       serial_id INTEGER NOT NULL,
       transaction_date DATE NOT NULL,
       transaction_type VARCHAR(10) NOT NULL,  -- 'Income' or 'Expense'
       category VARCHAR(50) NOT NULL,
       amount NUMERIC(15, 2) NOT NULL,
       total NUMERIC(15, 2),
       FOREIGN KEY (serial_id) REFERENCES customer(serial_id) ON DELETE CASCADE
      );
      ```
      ```bash
      CREATE TABLE budgets (
       budget_id SERIAL PRIMARY KEY,
       serial_id INTEGER NOT NULL,
       category VARCHAR(50) NOT NULL,
       limit NUMERIC(15, 2) NOT NULL,
       spent NUMERIC(15, 2) DEFAULT 0,
       remaining NUMERIC(15, 2),
       FOREIGN KEY (serial_id) REFERENCES customer(serial_id) ON DELETE CASCADE
      );
      ```
6. Run the application:
   ```bash
   flask run
   ```
7. Open your browser and visit `http://127.0.0.1:5000`.

---

## Usage
- Register or log in to start tracking your budgets.
- Use features such as **Budget Goals**, **AI Budget Recommendations**, **Transactions Manager**, and the **Statement Analyzer**.
- Read finance articles for tips.
- Ask questions to the integrated **chatbot** for quick support.

---

## Screenshots
- **Login and SignUp Page** ![image](https://github.com/user-attachments/assets/f9f7821b-0644-4dcc-840a-281b4c726d55)
- **Home page** ![image](https://github.com/user-attachments/assets/71a8e902-8ecd-4a26-9fd2-64e58215142e)
- **Statement Analyzer** ![image](https://github.com/user-attachments/assets/f97f9eb9-2453-4ea4-a4ba-325d20b23aff) ![image](https://github.com/user-attachments/assets/10722c33-64f9-4866-9235-d7fa4b99c361)
- **Finance Tracker**![image](https://github.com/user-attachments/assets/7247967f-f78f-4c98-8ac7-04a3ab3a9f91) ![image](https://github.com/user-attachments/assets/baa2da32-ac5f-4a19-b10f-f0611f6113a1)
- **Analysis** ![image](https://github.com/user-attachments/assets/114754aa-ca4f-4a12-9116-cfeb38f0bf43)
- **Budget Goals** ![image](https://github.com/user-attachments/assets/98f3b911-7b7f-48ca-96f6-c34fa32a11be) ![image](https://github.com/user-attachments/assets/8c945efd-c2fd-4608-8286-da3045dd162b)
- **Articles** ![image](https://github.com/user-attachments/assets/10f88bac-9962-4670-8bb9-e1eb633bce14)
- **Chatbot** ![image](https://github.com/user-attachments/assets/4afd8a5a-d5af-4ff1-8db7-4e325ecedf5a)
---

## Contributors
We thank the following people for their contributions to this project:

- **Archana K M** - (https://github.com/Archana-K-M)
- **Anirudhh S** - (https://github.com/rudhhstoic)
- **Devanidharsan K** - (https://github.com/Deva399212)
- **Varsha G** - (https://github.com/Varshavishnu)

---

## Contact
For any inquiries or feedback, reach out to:

- **Archana K M**
- **Email**: archanakm297@gmail.com
- **GitHub**: (https://github.com/Archana-K-M)
---


