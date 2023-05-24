# app.py

import os
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

DEV = os.getenv("FLASK_ENV", "development") == "development"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/hello-world', methods=['GET'])
@cross_origin()
def hello():
    dummy_data = {
        'id': 0,
        'name': 'Hello World',
        'path': 'https://akademik.itb.ac.id',
        'predicted_role': 'Java Developer',
        'timestamp': '2023-04-15 10:51:38.843929'
    }
    return jsonify({'data': [dummy_data]})

if __name__ == '__main__':
    app.run(debug=DEV)