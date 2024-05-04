from flask import Flask, request, send_file
from pymongo import MongoClient
import os

app = Flask(__name__)
@app.route('/')
def index():
    return 'Welcome to your Flask application!'


@app.route('/get_pdf', methods=['GET'])
def get_pdf():
    filename = request.args.get('filename')
    if not filename:
        return 'Error: Missing filename parameter', 400
    
    # Read MongoDB URI from file
    with open('data.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.mydatabase  # Replace 'mydatabase' with your database name
    collection = db.pdf_data

    # Download the PDF File from MongoDB Atlas
    query = {"filename": filename}
    pdf_document = collection.find_one(query)
    if pdf_document:
        pdf_data = pdf_document["data"]
        return send_file(pdf_data, as_attachment=True, attachment_filename=f'{filename}.pdf')
    else:
        return 'Error: PDF document not found', 404
