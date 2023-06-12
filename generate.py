from system.major import *
from system.cf_calculation import *

if __name__ == '__main__':
    # Query
    major = "MIF"
    start_date = "2023-04-10"
    end_date = "2023-04-10"

    print("Start Date:", start_date)
    print("End Date:", end_date)

    df_schedule_nim, df_dates = major_filter_period(major, start_date, end_date)
    print(df_schedule_nim.tail(5), len(df_schedule_nim))
    print(df_dates.tail(5), len(df_dates))
    print(category_distribution(df_dates))
    print(in_class_out_class(df_dates))
    print(activity_distribution(df_dates, df_schedule_nim))
    print(get_courses_distribution(df_schedule_nim))