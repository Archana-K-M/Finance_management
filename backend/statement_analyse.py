from flask import Flask, request, jsonify
import pandas as pd
import os
from statement import read_and_concat_tables
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Function to process DOCX file and return data

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Must upload a file and select the bank name"}), 400

    file = request.files['file']
    input_text = request.form['text']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Process the DOCX file
    combined_df, recommend = read_and_concat_tables(file_path, input_text.lower())
    os.remove(file_path)  # Clean up the file

    recommend_message = recommend['overall_recommendations'][0]  # Extract the message string
    recommend_df = recommend['monthly_recommendations']
    combined_df = combined_df.applymap(lambda x: str(x) if isinstance(x, pd.Period) else x)
    recommend_df = recommend_df.applymap(lambda x: str(x) if isinstance(x, pd.Period) else x)
    
    # Convert DataFrame to JSON and return
    data_json = combined_df.to_dict(orient="records")
    recommend_data = recommend_df.to_dict(orient="records")

    total_credit_values = [entry.get('total_credit', 0) for entry in recommend_data if isinstance(entry.get('total_credit', None), (int, float))]
    average_total_credit = sum(total_credit_values) / len(total_credit_values) if total_credit_values else 0

    return jsonify(data=data_json, recommend_message=recommend_message, recommend_data=recommend_data, average_total_credit=average_total_credit) # if monthly analysis too needed give--> return jsonify(data=data_json, recommend_message=recommend_message, recommend_data=recommend_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 5000)
