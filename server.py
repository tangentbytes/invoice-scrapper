from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from typing import Any
from docquery import document, pipeline
import base64
p = pipeline('document-question-answering')

app = Flask(__name__)

# database connection #TODO: move to instance/config file ==> to hide secrets
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 
db=SQLAlchemy(app)
app.app_context().push()


# Define the model representing your PostgreSQL table
@dataclass
class FileData(db.Model):
    __tablename__ = 'file_data'

    id: int
    userId:str 
    fileName:str
    timeStamp:str
    fileDump:Any

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    fileName = db.Column(db.String)
    timeStamp = db.Column(db.String)
    fileDump = db.Column(db.JSON)

def file_to_base64(file_path):
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()
            base64_encoded = base64.b64encode(file_content).decode("utf-8")
            return base64_encoded
    except FileNotFoundError:
        return None

# //todo
# API to get receipt
@app.route('/receipt/<userId>', methods=['GET'])
def get_receipt(userId):
    timestamp = request.args.get('date')
    # Implement logic to fetch receipt for the given user and date
    # For demonstration, let's just return a sample response

    if timestamp:
        # Fetch data by timestamp and user ID
        data = FileData.query.filter_by(userId=userId, timeStamp=timestamp).first()
        print("Data",data)
        base64_data = file_to_base64("files/"+data["fileName"])
        if data:
            return jsonify({"data":data,"image":base64_data})  # Assuming you have a serialize method in your model
        else:
            return jsonify({'message': 'Data not found for provided userId and timestamp'})
    else:
        # Fetch data only by user ID
        data = FileData.query.filter_by(userId=userId).all()
        print(data)
        base64_data = file_to_base64("files/"+data.fileName)
        if data:
            return jsonify({"data":data,"image":base64_data})  # Assuming you have a serialize method in your model
        else:
            return jsonify({'message': 'No data found for the provided userId'})

# API to delete receipt
@app.route('/receipt/<receiptId>', methods=['DELETE'])
def delete_receipt(receiptId):
    if receiptId:
        file_data = FileData.query.filter_by(id=receiptId).first()
        if file_data:
            db.session.delete(file_data)
            db.session.commit()
            return jsonify({'message': f'Data with fileName {receiptId} deleted successfully'})
        else:
            return jsonify({'message': f'No data found for fileName {receiptId}'})
    else:
        return jsonify({'message': 'Please provide fileName to delete data'})

# API to extract data from image
@app.route('/extract/<userId>', methods=['POST'])
def extract_data_from_image(userId):
    if 'file' in request.files:
        # store file to server
        file = request.files["file"]
        if file.filename == "":
            return "No selected file",400
        
        file_content = file.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        timeStamp=datetime.now().isoformat()
        fileName=timeStamp + file.filename
        file.save('files/'+fileName)

        # TODO: call python function
        doc = document.load_document("ewe.png")
        lsit = ['InvoiceNumber', 'total', 'date', 'merchant','currency']
        data = {}
        questions = [
            "What is the invoice number?",
            "What is the invoice total",
            "What is the date",
            "What is the Merchant name",
        ]

        for i,question in enumerate(questions):
            result = p(question=question, **doc.context)[0]
            print(i,question)    
            data[lsit[i]] = result['answer']

        print(data)
        data['file'] = base64_content
        mlResponse=data 
        # extractedData={"userId":userId,"fileName":fileName,"timeStamp":timeStamp,"fileDump":mlResponse}

        new_file_data = FileData(
            userId=userId,
            fileName=fileName,
            timeStamp=timeStamp,
            fileDump=mlResponse,
        )

        db.session.add(new_file_data)
        db.session.commit()

        return jsonify(new_file_data)
    else:
        return jsonify({"error": "No image found in the request"}), 400

# API to save receipt
@app.route('/receipt', methods=['POST'])
def save_receipt():
    if request.json:
        attributes=request.get_json()

        new_file_data = FileData(
            userId=attributes["userId"],
            fileName=attributes["fileName"],
            timeStamp=datetime.now().isoformat(),
            fileDump=attributes["fileDump"]
        )

        db.session.add(new_file_data)
        db.session.commit()

        return jsonify(new_file_data)
        
        return jsonify({"message": "Receipt saved"})
    else:
        return jsonify({"error": "No data received"}), 400

# API to edit receipt
@app.route('/receipt', methods=['PUT'])
def edit_receipt():
    attributes=request.get_json()
    user_id = attributes['userId']
    file_name = attributes['fileName']
    attributes_to_update = request.get_json()

    if user_id and file_name and attributes_to_update:
        file_data = FileData.query.filter_by(userId=user_id, fileName=file_name).first()
        if file_data:
            for key, value in attributes_to_update.items():
                if hasattr(file_data, key):
                    setattr(file_data, key, value)

            db.session.commit()
            return jsonify({'message': 'FileData updated successfully'})
        else:
            return jsonify({'message': 'Data not found for provided userId and fileName'})
    else:
        return jsonify({'message': 'Please provide userId, fileName, and attributes to update'})

if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()  # Create tables based on the models
