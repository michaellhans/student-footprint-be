from system.major import *
from system.cf_calculation import *

def overall_pipeline(start_date, end_date):
    # Phase 1: Carbon Footprint Calculation
    df_schedule, df_dates = all_filter_period(start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule)
    cf_course_distribution = get_courses_distribution(df_schedule).to_dict(orient='records')

    # Phase 2: Predictive Modeling Fit and Predict
    y_test, y_pred = fit_and_predict(df_predictive, start_date, get_forecasting_date(start_date, end_date))
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    # Phase 3: Combine with the CF History
    y_test = y_test.reset_index(name='real')
    y_test['predicted_emission'] = y_pred
    df_model = df_dates.groupby('date').sum().reset_index()
    print(df_model.dtypes)
    print(y_test.dtypes)
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model.to_dict(orient='records')

    # Debugging purpose: show all regression test parameters
    print(df_model[['total_emission', 'predicted_emission']])
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("R2 Score:", r2)
    print("MAPE:", mape)

    return {
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

def major_pipeline(major, start_date, end_date):
    # Phase 1: Carbon Footprint Calculation
    df_schedule, df_dates = major_filter_period(major, start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule)
    cf_course_distribution = get_courses_distribution(df_schedule).to_dict(orient='records')

    # Phase 2a: Predictive Modeling Preparation
    master_df_schedules = DB_INSTANCE.master_df_schedules
    master_df_dates = DB_INSTANCE.master_df_dates
    dfx = master_df_dates[master_df_dates['NIM'].astype(str).str.startswith(code[major])]
    dfy = master_df_schedules[master_df_schedules['NIM'].astype(str).str.startswith(code[major])]
    df = prepare_predictive_dataset(dfx, dfy, DB_INSTANCE.df_electricity_bills, DB_INSTANCE.df_survey)

    # Phase 2b: Predictive Modeling Fit and Predict
    y_test, y_pred = fit_and_predict(df, start_date, get_forecasting_date(start_date, end_date), option=major)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    # Phase 3: Combine with the CF History
    y_test = y_test.reset_index(name='real')
    y_test['predicted_emission'] = y_pred
    df_model = df_dates.groupby('date').sum().reset_index()
    y_test['date'] = y_test['date'].dt.strftime('%Y-%m-%d')
    print(df_model.dtypes)
    print(y_test.dtypes)
    print(y_test)
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model.to_dict(orient='records')

    # Debugging purpose: show all regression test parameters
    print(df_model[['total_emission', 'predicted_emission']])
    print("MAE:", mae)
    print("RMSE:", rmse)
    print("R2 Score:", r2)
    print("MAPE:", mape)

    return {
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

# def student_pipeline(NIM, start_date, end_date):
#     continue

if __name__ == '__main__':
    # Query
    major = "IF"
    NIM = 13520115
    start_date = "2023-01-16"
    end_date = "2023-02-10"

    print("Start Date:", start_date)
    print("End Date:", end_date)

    overall_pipeline(start_date, end_date)
    major_pipeline(major, start_date, end_date)
    major_pipeline("STI", start_date, end_date)    
    major_pipeline("MIF", start_date, end_date)

    # df_schedule_nim, df_dates = major_filter_period(major, start_date, end_date)
    # print(df_schedule_nim.tail(5), len(df_schedule_nim))
    # print(df_dates.tail(5), len(df_dates))
    # print(category_distribution(df_dates))
    # print(in_class_out_class(df_dates))
    # print(activity_distribution(df_dates, df_schedule_nim))
    # print(get_courses_distribution(df_schedule_nim))
    # df_schedule = DB_INSTANCE.master_df_schedules
    # df_dates = DB_INSTANCE.master_df_dates
    # df_schedule_nim = df_schedule[df_schedule['NIM'].astype(str).str.startswith(code[major])]
    # dfx = df_dates[df_dates['NIM'].astype(str).str.startswith(code[major])]
    # df = prepare_predictive_dataset(dfx, df_schedule_nim, DB_INSTANCE.df_electricity_bills, DB_INSTANCE.df_survey)
    # y_pred, y_test = fit_and_predict(df, start_date, end_date)
    # mae = mean_absolute_error(y_test, y_pred)
    # rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    # r2 = r2_score(y_test, y_pred)
    # mape = mean_absolute_percentage_error(y_test, y_pred)

    # y_test = y_test.reset_index(name='real')
    # y_test['prediction'] = y_pred
    # print(y_test)
    # print("MAE:", mae)
    # print("RMSE:", rmse)
    # print("R2 Score:", r2)
    # print("MAPE:", mape)
