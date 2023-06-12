import pandas as pd
from datetime import datetime, timedelta
from .utils import *
from .database import DB_INSTANCE

# GLOBAL VARIABLE ACCESSED FROM DB
master_df_dates = DB_INSTANCE.master_df_dates
master_df_schedules = DB_INSTANCE.master_df_schedules

code = {
    "IF": "135",
    "STI": "182",
    "MIF": "235"
}

def major_filter_period(major, start_date, end_date):
    df_schedule_filtered = master_df_schedules[(master_df_schedules['NIM'].astype(str).str.startswith(code[major])) &
        (master_df_schedules['date'] >= start_date) & (master_df_schedules['date'] <= end_date)].copy()
    df_dates_filtered = master_df_dates[(master_df_dates['NIM'].astype(str).str.startswith(code[major])) &
        (master_df_dates['date'] >= start_date) & (master_df_dates['date'] <= end_date)].copy()
    return df_schedule_filtered, df_dates_filtered

def all_filter_period(start_date, end_date):
    df_schedule_filtered = master_df_schedules[(master_df_schedules['date'] >= start_date) & (master_df_schedules['date'] <= end_date)].copy()
    df_dates_filtered = master_df_dates[(master_df_dates['date'] >= start_date) & (master_df_dates['date'] <= end_date)].copy()
    return df_schedule_filtered, df_dates_filtered

def get_courses_distribution(df_schedules):
    return df_schedules.groupby('course_id')['emission'].sum().reset_index().sort_values(by='emission', ascending=False)
