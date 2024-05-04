from flask import Flask, request, send_file
from pymongo import MongoClient
import os

app = Flask(__name__)
@app.route('/get_pdf', methods=['GET'])
def get_pdf():
    filename = request.args.get('filename')
    if not filename:
        return 'Error: Missing filename parameter', 400
    
    # Connect to MongoDB Atlas
    mongodb_uri = os.environ.get('MONGODB_URI')
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
