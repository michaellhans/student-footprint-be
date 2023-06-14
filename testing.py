from system.major import *
from system.cf_calculation import *
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def students_summary(start_date, end_date):
    _, df_dates = all_filter_period(start_date, end_date)
    df_dates = df_dates.groupby('NIM').sum().reset_index()
    df_dates = df_dates.astype({'NIM': int})

    return df_dates[['NIM', 'courses_emission', 'commuting_emission', 'outclass_emission', 'total_emission']].to_dict(orient='records')

def major_summary(start_date, end_date):
    _, df_dates = all_filter_period(start_date, end_date)
    df_dates = df_dates.groupby('date').sum().reset_index()
    df_dates = df_dates[['date', 'total_emission']]
    majors = ['IF', 'STI', 'MIF']
    for major in majors:
        _, dfx = major_filter_period(major, start_date, end_date)
        dfx = dfx.groupby('date').sum().reset_index()
        dfx = dfx.rename(columns={'total_emission': major})
        df_dates = pd.merge(df_dates, dfx[['date', major]], on='date', how='left')

    df_dates.fillna(0, inplace=True)
    return df_dates[['date', 'total_emission', 'IF', 'STI', 'MIF']].to_dict(orient='records')

def overall_pipeline(start_date, end_date):
    # Phase 1: Carbon Footprint Calculation
    df_schedule, df_dates = all_filter_period(start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule)
    cf_course_distribution = get_courses_distribution(df_schedule).to_dict(orient='records')
    df_predictive.index = pd.to_datetime(df_predictive.index, format="%Y-%m-%d")

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
    y_test['date'] = y_test['date'].dt.strftime('%Y-%m-%d')
    print(y_test.tail(10))
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model[['date', 'courses_emission', 'commuting_emission', 'outclass_emission', 'total_emission', 'predicted_emission']].to_dict(orient='records')

    # Debugging purpose: show all regression test parameters
    print(df_model.head(1))
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
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

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
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model[['date', 'courses_emission', 'commuting_emission', 'outclass_emission', 'total_emission', 'predicted_emission']].to_dict(orient='records')

    # Debugging purpose: show all regression test parameters
    print(df_model.head(1))
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

def student_pipeline(NIM, start_date, end_date):
    # Phase 1: Carbon Footprint Calculation
    df_schedule, df_dates = student_calculation(NIM, start_date, end_date)
    cf_category = category_distribution(df_dates)
    cf_in_out = in_class_out_class(df_dates)
    cf_activity = activity_distribution(df_dates, df_schedule)
    select_cols = ["NIM", "name", "major", "semester", "gender", "mode_transportation", "residence",
                   "travel_time", "distance", "stay_on_campus", "use_laptop_on_class", "num_of_devices",
                   "day_laptop_total", "day_laptop_outclass", "day_phone_total", "paper_consumption",
                   "pandemic_AC_frequent", "pandemic_day_laptop_total", "pandemic_day_laptop_outclass", "pandemic_day_phone_total"]
    cf_profile = df_survey[df_survey['NIM'] == NIM].iloc[0][select_cols].to_dict()

    # Phase 2a: Predictive Modeling Preparation
    master_df_schedules = DB_INSTANCE.master_df_schedules
    master_df_dates = DB_INSTANCE.master_df_dates
    dfx = master_df_dates[master_df_dates['NIM'] == NIM]
    dfy = master_df_schedules[master_df_schedules['NIM'] == NIM]
    df = prepare_predictive_dataset(dfx, dfy, DB_INSTANCE.df_electricity_bills, DB_INSTANCE.df_survey)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%d")

    # Phase 2b: Predictive Modeling Fit and Predict
    y_test, y_pred = fit_and_predict(df, start_date, get_forecasting_date(start_date, end_date), option='student')
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    # Phase 3: Combine with the CF History
    y_test = y_test.reset_index(name='real')
    y_test['predicted_emission'] = y_pred
    df_model = df_dates.groupby('date').sum().reset_index()
    y_test['date'] = y_test['date'].dt.strftime('%Y-%m-%d')
    df_model = pd.merge(df_model, y_test[['date', 'predicted_emission']], how='left')
    cf_history = df_model[['date', 'courses_emission', 'commuting_emission', 'outclass_emission', 'total_emission', 'predicted_emission']].to_dict(orient='records')

    # Debugging purpose: show all regression test parameters
    print(df_model.head(1))
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
            "cf_profile": cf_profile
        }
    }

if __name__ == '__main__':
    # Query
    major = "IF"
    NIM = 13520115
    start_date = "2023-01-16"
    end_date = "2023-05-30"

    print("Start Date:", start_date)
    print("End Date:", end_date)

    overall_pipeline(start_date, end_date)
    # major_pipeline(major, start_date, end_date)
    # major_pipeline("STI", start_date, end_date)    
    # major_pipeline("MIF", start_date, end_date)
    # student_pipeline(13520115, start_date, end_date)

    # major_summary(start_date, end_date)
    # students_summary(start_date, end_date)