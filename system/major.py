import pandas as pd
from .utils import *
from .database import DB_INSTANCE
from sklearn.linear_model import LinearRegression

# GLOBAL VARIABLE ACCESSED FROM DB
master_df_dates = DB_INSTANCE.master_df_dates
master_df_schedules = DB_INSTANCE.master_df_schedules
df_courses = DB_INSTANCE.df_courses
df_predictive = DB_INSTANCE.df_predictive

code = {
    "IF": "135",
    "STI": "182",
    "MIF": "235"
}

# Filter the master_df_schedules and master_df_dates by major, start_date, and end_date
def major_filter_period(major, start_date, end_date):
    df_schedule_filtered = master_df_schedules[(master_df_schedules['NIM'].astype(str).str.startswith(code[major])) &
        (master_df_schedules['date'] >= start_date) & (master_df_schedules['date'] <= end_date)].copy()
    df_dates_filtered = master_df_dates[(master_df_dates['NIM'].astype(str).str.startswith(code[major])) &
        (master_df_dates['date'] >= start_date) & (master_df_dates['date'] <= end_date)].copy()
    return df_schedule_filtered, df_dates_filtered

# Filter the master_df_schedules and master_df_dates by start_date and end_date
def all_filter_period(start_date, end_date):
    df_schedule_filtered = master_df_schedules[(master_df_schedules['date'] >= start_date) & (master_df_schedules['date'] <= end_date)].copy()
    df_dates_filtered = master_df_dates[(master_df_dates['date'] >= start_date) & (master_df_dates['date'] <= end_date)].copy()
    return df_schedule_filtered, df_dates_filtered

# Get courses emission distribution
def get_courses_distribution(df_schedules):
    dfx = df_schedules.groupby('course_id')['emission'].sum().reset_index().sort_values(by='emission', ascending=False)
    dfx = pd.merge(dfx, df_courses[["course_id", "course_name", "exam_paper_based", "class_electronic"]], on ='course_id')
    return dfx

# Prepare the predictive dataset for predictive analytics modeling
def prepare_predictive_dataset(df, df_schedule, df_electricity_bills, df_survey):
    dfx = pd.DataFrame(index=df_schedule['date'].unique()).sort_index()
    dfx['total_classes'] = df_schedule.groupby('date')['key'].nunique()
    dfx['online_classes'] = df_schedule[df_schedule['is_online'] == 'Online'].groupby('date')['key'].nunique()
    dfx['offline_classes'] = df_schedule[~(df_schedule['is_online'] == 'Online')].groupby('date')['key'].nunique()
    dfx['students_attends'] = df_schedule.groupby('date')['NIM'].nunique()
    dfx.index = pd.to_datetime(dfx.index)
    dfx['is_exam_period'] = (dfx.index.month.isin([5, 12])).astype(bool)
    dfx.fillna(0, inplace=True)
    df = pd.merge(df, df_survey[['NIM', 'day_laptop_total', 'distance']], on ='NIM')
    df = df.groupby('date').sum().reset_index()[['date', 'courses_emission', 'commuting_emission', 'outclass_emission', 'total_emission', 'online_day', 'day_laptop_total', 'distance']]

    dfx = dfx.reset_index().rename(columns={'index': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df = pd.merge(df, dfx, on=['date'])

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df_electricity_bills['year'] = pd.to_datetime(df_electricity_bills['Date']).dt.year
    df_electricity_bills['month'] = pd.to_datetime(df_electricity_bills['Date']).dt.month

    df = pd.merge(df, df_electricity_bills[['year', 'month', 'Energy']], on=['year', 'month'], how='left')
    df['kWh_day'] = df['Energy'] / pd.to_datetime(df['date']).dt.days_in_month
    df = df.drop(['year', 'month', 'Energy'], axis=1)
    df = df.fillna(method='ffill')
    df = df.set_index(df.columns[0])
    df = df.resample('1D').mean()
    df = df.interpolate(option='spline')

    select_cols = ['total_emission', 'online_day', 'day_laptop_total', 'distance', 'kWh_day', 'total_classes', 'online_classes', 'offline_classes', 'students_attends', 'is_exam_period']
    df = df[select_cols]

    return df

# Create the predictive analytics or use the existing one and predict the testing data
def fit_and_predict(df, start_date, end_date, option=None):
    # Create lagged versions of the variables with three lags
    lags = 30
    columns = df.columns
    lagged_data = df.copy()
    for i in range(1, lags+1):
        lagged_data[f'total_emission_lag{i}'] = lagged_data['total_emission'].shift(i)

    # Remove rows with NaN values due to shifting
    lagged_data = lagged_data.dropna()

    # Split the data into input features (X) and target variable (y)
    X = lagged_data.drop(['total_emission'], axis=1)
    y = lagged_data[columns[0]]  # Example: Using first column (total emission) as the target variable

    # Split the data into training and testing sets (e.g., 80% for training, 20% for testing)
    train_size = int(len(X) * 0.8)
    X_train = X[:train_size]
    y_train = y[:train_size]
    X_test = X[(X.index >= start_date) & (X.index <= end_date)]
    y_test = y[(y.index >= start_date) & (y.index <= end_date)]

    model = DB_INSTANCE.itb_model
    if (option == "IF"):
        model = DB_INSTANCE.if_model
    elif (option == "STI"):
        model = DB_INSTANCE.sti_model
    elif (option == "MIF"):
        model = DB_INSTANCE.mif_model
    elif (option == "student"):
        model = LinearRegression().fit(X_train, y_train)

    y_pred = model.predict(X_test)

    return y_test, y_pred

