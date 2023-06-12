import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from system.cf_calculation import activity_distribution, category_distribution, in_class_out_class, student_calculation

# Get the parent directory of 'app.py'
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

DEV = os.getenv("FLASK_ENV", "development") == "development"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Route to test if the service is alive or not
@app.route('/hello-world', methods=['GET'])
@cross_origin()
def hello():
    users = [{'NIM': 13518056, 'name': 'Michael Hans'}, {'NIM': 23522011, 'name': 'Michael Hans'}]
    return jsonify({'data': users})

# Route to retrieve student carbon footprint
@app.route('/student', methods=['GET'])
@cross_origin()
def student():
    NIM = int(request.args.get('NIM'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Process the data using the provided input
    print("NIM:", NIM, end="; ")
    print("Start Date:", start_date, end="; ")
    print("End Date:", end_date)

    df_schedule_nim, df_dates = student_calculation(NIM, start_date, end_date)
    # print(df_schedule_nim.tail(5))
    # print(df_dates.tail(5))
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule_nim)
    cf_history = df_dates.to_dict(orient='records')

    # Example response
    response = {
        'NIM': NIM,
        'start_date': start_date,
        'end_date': end_date,
        'details': {
            "cf_category": {
                'category': list(cf_category.keys()),
                'value': list(cf_category.values())
            },
            "cf_in_out": {
                'category': list(cf_in_out.keys()),
                'value': list(cf_in_out.values())
            },
            "cf_activity": {
                'category': list(cf_activity.keys()),
                'value': list(cf_activity.values())
            },
            "cf_history": cf_history
        }
    }

    return jsonify({'data': response})


if __name__ == '__main__':
    app.run(debug=DEV)