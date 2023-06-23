import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from system.utils import *
from testing import itb_statistics, major_pipeline, major_summary, overall_pipeline, student_pipeline, students_summary

# Get the parent directory of 'app.py'
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)
DEV = os.getenv("FLASK_ENV", "development") == "development"
app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# ================================== ENDPOINT ====================================================
# Route to test if the service is alive or not
@app.route('/hello-world', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def hello():
    users = [{'NIM': 13518056, 'name': 'Michael Hans'}, {'NIM': 23522011, 'name': 'Michael Hans'}]
    response = jsonify({'data': users})
    return response

# Route to retrieve student carbon footprint
@app.route('/student', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def student():
    NIM = int(request.args.get('NIM'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Debugging purpose
    debugging_api(NIM, start_date, end_date)

    payload = student_pipeline(NIM, start_date, end_date)
    response = jsonify({'data': payload})

    return response

# Route to retrieve major carbon footprint
@app.route('/major', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def major():
    major = request.args.get('major')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Debugging purpose
    debugging_api(major, start_date, end_date)

    payload = major_pipeline(major, start_date, end_date)
    response = jsonify({'data': payload})

    return response

# Route to retrieve major carbon footprint
@app.route('/itb', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def itb():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Debugging purpose
    debugging_api("itb", start_date, end_date)

    payload = overall_pipeline(start_date, end_date)
    response = jsonify({'data': payload})

    return response

# Route to retrieve carbon footprint summary
@app.route('/summary', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def summary():
    level = request.args.get('level')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Debugging purpose
    debugging_api(level, start_date, end_date)

    payload = None
    if (level == 'student'):
        payload = students_summary(start_date, end_date)
    elif (level == 'stats'):
        payload = itb_statistics(start_date, end_date)
    else:
        payload = major_summary(start_date, end_date)

    response = jsonify({'data': payload})

    return response

if __name__ == '__main__':
    app.run(debug=DEV)