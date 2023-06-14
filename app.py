import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from system.cf_calculation import activity_distribution, category_distribution, in_class_out_class, student_calculation
from system.major import all_filter_period, fit_and_predict, get_courses_distribution, major_filter_period, df_predictive
from system.utils import *

# Get the parent directory of 'app.py'
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(parent_dir)

DEV = os.getenv("FLASK_ENV", "development") == "development"
app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})
app.config['CORS_HEADERS'] = 'Content-Type'

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

    # Process the data using the provided input
    print("NIM:", NIM, end="; ")
    print("Start Date:", start_date, end="; ")
    print("End Date:", end_date)

    df_schedule_nim, df_dates = student_calculation(NIM, start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule_nim)
    cf_history = df_dates.to_dict(orient='records')

    # Example response
    payload = {
        'NIM': NIM,
        'start_date': start_date,
        'end_date': end_date,
        'details': {
            "cf_category": cf_category,
            "cf_in_out": cf_in_out,
            "cf_activity": cf_activity,
            "cf_history": cf_history
        }
    }

    response = jsonify({'data': payload})

    return response

# Route to retrieve major carbon footprint
@app.route('/major', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def major():
    major = request.args.get('major')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Process the data using the provided input
    print("major:", major, end="; ")
    print("Start Date:", start_date, end="; ")
    print("End Date:", end_date)

    df_schedule_nim, df_dates = major_filter_period(major, start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule_nim)
    cf_history = df_dates.groupby('date').sum().reset_index().to_dict(orient='records')
    cf_course_distribution = get_courses_distribution(df_schedule_nim).to_dict(orient='records')

    # Example response
    payload = {
        'major': major,
        'start_date': start_date,
        'end_date': end_date,
        'details': {
            "cf_category": cf_category,
            "cf_in_out": cf_in_out,
            "cf_activity": cf_activity,
            "cf_history": cf_history,
            "cf_course_distribution": cf_course_distribution
        }
    }

    response = jsonify({'data': payload})

    return response

# Route to retrieve major carbon footprint
@app.route('/itb', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def itb():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Process the data using the provided input
    print("Start Date:", start_date, end="; ")
    print("End Date:", end_date)

    df_schedule_nim, df_dates = all_filter_period(start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule_nim)

    # Predictive modeling
    y_pred, y_test = fit_and_predict(df_predictive, start_date, end_date)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    print(len(y_test))
    print(len(y_pred))
    y_test = y_test.reset_index(name='real')
    y_test['predicted_emission'] = y_pred
    df_model = df_dates.groupby('date').sum().reset_index()
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model.to_dict(orient='records')

    print(df_model[['total_emission', 'predicted_emission']])

    cf_course_distribution = get_courses_distribution(df_schedule_nim).to_dict(orient='records')

    # Example response
    payload = {
        'start_date': start_date,
        'end_date': end_date,
        'details': {
            "cf_category": cf_category,
            "cf_in_out": cf_in_out,
            "cf_activity": cf_activity,
            "cf_history": cf_history,
            "cf_course_distribution": cf_course_distribution
        }
    }

    response = jsonify({'data': payload})

    return response

if __name__ == '__main__':
    app.run(debug=DEV)