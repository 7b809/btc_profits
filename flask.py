from flask import Flask, render_template, send_file
from pymongo import MongoClient
import os

app = Flask(__name__)

# Connect to MongoDB Atlas
mongodb_uri = 'mongodb+srv://ej818793:dA2Jum3EipkJgVUf@btcprofits.ss1iqtf.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(mongodb_uri)
db = client.mydatabase  # Replace 'mydatabase' with your database name
collection = db.pdf_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download-pdf')
def download_pdf():
    query = {"filename": "testing_one.pdf"}
    pdf_document = collection.find_one(query)
    if pdf_document:
        pdf_data = pdf_document["data"]
        with open("downloaded_pdf.pdf", "wb") as f:
            f.write(pdf_data)
        return send_file("downloaded_pdf.pdf", as_attachment=True)
    else:
        return "PDF document not found in MongoDB Atlas."

if __name__ == '__main__':
    app.run(debug=True)
