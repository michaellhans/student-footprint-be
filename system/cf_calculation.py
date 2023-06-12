import pandas as pd
from datetime import datetime, timedelta
from .utils import *
from .database import DB_INSTANCE

# GLOBAL VARIABLE ACCESSED FROM DB
df_participants = DB_INSTANCE.df_participants
df_schedule = DB_INSTANCE.df_schedule
df_class_count = DB_INSTANCE.df_class_count
df_practicum = DB_INSTANCE.df_practicum
df_survey = DB_INSTANCE.df_survey

def get_year_semester(date):
    # Split the date into year, month, and day components
    year, month, day = date.split('-')

    # Convert the components to integers
    year = int(year)
    month = int(month)
    day = int(day)

    # Determine the year and semester based on the month
    if month >= 7 and month <= 12:
        year_of_study = year
        semester = 1
    elif month >= 1 and month <= 6:
        year_of_study = year - 1
        semester = 2

    # Return the result as a dictionary
    return {'year': year_of_study, 'semester': semester}

from datetime import datetime

def time_difference_in_hours(time1, time2):
    # Convert time strings to datetime objects
    format_str = "%H:%M"
    datetime1 = datetime.strptime(time1, format_str)
    datetime2 = datetime.strptime(time2, format_str)

    # Calculate the time difference in hours
    time_diff = datetime2 - datetime1
    hours = time_diff.total_seconds() / 3600
    return hours

activity_group = {
    "Course": ['Kuliah', 'Kuis', 'Tutorial'],
    "Exam": ['UAS', 'UTS'],
    "Practicum": ['Praktikum']
}

def get_activity_group(input_value):
    for key, value_list in activity_group.items():
        if input_value in value_list:
            return key
    return None

def commuting_counter(df_temp, date):
    # Initialize a counter for the gaps
    gap_counter = 0

    # Iterate over the rows
    for i in range(1, len(df_temp)):
        prev_end_time = df_temp.iloc[i - 1]['end_time']
        next_start_time = df_temp.iloc[i]['start_time']

        # Calculate the time difference
        time_diff = next_start_time - prev_end_time

        # Check if the time difference is approximately 3 hours (within a certain threshold)
        if abs(time_diff - timedelta(hours=3)) <= timedelta(minutes=15):
            gap_counter += 1

    # print("Number of approximately 3-hour gaps:", gap_counter)
    return gap_counter

def courses_schedule_calculation(df_schedule_nim, df_survey_nim, online_method):
    df_schedule_nim['emission'] = 0
    df_schedule_nim['electricity'] = 0
    df_schedule_nim['classroom'] = 0
    df_schedule_nim['paper'] = 0
    paper_consumption = df_survey_nim['paper_consumption'].values[0]
    use_laptop_on_class = df_survey_nim['use_laptop_on_class'].values[0]
    num_of_devices = df_survey_nim['num_of_devices'].values[0]

    for index, row in df_schedule_nim.iterrows():
        # Get the activity 
        activity = get_activity_group(row['activity'])

        # Get duration of the lecture / practicum / exam
        course_duration = time_difference_in_hours(row['start_time'],  row['end_time'])

        # Check if the session is online / offline
        isOnline = (row['is_online'] == "Online") or online_method
        
        # If is online, calculate directly with pandemic formula
        if (isOnline):
          df_schedule_nim.at[index, 'electricity'] = electronic_emission(laptop_power, course_duration)
          df_schedule_nim.at[index, 'emission'] = df_schedule_nim.at[index, 'electricity']
          continue
        
        # If is offline, calculate using the classroom emission factor
        else:
          # Both of them use the emission generated from the classroom
          location = row['location']
          total_emission = classroom_emission(location, course_duration) / row['counts']
          df_schedule_nim.at[index, 'classroom'] = total_emission
          isPaperBased = True # change with from the exam list of paper based exam

          # 2nd Alternative
          if (activity == "Exam"):
            # If it was paper based, calculate the paper-based exam
            if (isPaperBased):
              total_emission += paper_emission(5)
              df_schedule_nim.at[index, 'paper'] += paper_emission(5)

            # If it was not, calculate the laptop usage within the duration
            else:
              total_emission += electronic_emission(laptop_power, course_duration)
              df_schedule_nim.at[index, 'electricity'] += electronic_emission(laptop_power, course_duration)

          elif (activity == "Course"):
            # Calculate the emission from paper usage
            # Calculate the emssion from electricity if the student use the electronic device
            # Add extra emission if the number of devices is more than one
            total_emission += paper_emission(paper_consumption)
            df_schedule_nim.at[index, 'paper'] += paper_emission(paper_consumption)
            if (use_laptop_on_class):
              total_emission += electronic_emission(laptop_power, course_duration)
              df_schedule_nim.at[index, 'electricity'] += electronic_emission(laptop_power, course_duration)

            if (num_of_devices >= 2):
              total_emission += electronic_emission(smartphone_power, course_duration)
              df_schedule_nim.at[index, 'electricity'] += electronic_emission(smartphone_power, course_duration)

          # If practicum, it has already included in the classroom emission factor
          df_schedule_nim.at[index, 'emission'] = total_emission
    
    return df_schedule_nim

def day_calculation(df_schedule_nim, df_survey_nim, online_method):
    pandemic_AC_frequent = df_survey_nim['pandemic_AC_frequent'].values[0]

    pandemic_day_laptop_total = int(df_survey_nim['pandemic_day_laptop_total'].values[0])
    pandemic_day_laptop_outclass = int(df_survey_nim['pandemic_day_laptop_outclass'].values[0])
    pandemic_day_phone_total = int(df_survey_nim['pandemic_day_laptop_total'].values[0])

    day_laptop_total = int(df_survey_nim['day_laptop_total'].values[0])
    day_laptop_outclass = int(df_survey_nim['day_laptop_outclass'].values[0])
    day_phone_total = int(df_survey_nim['day_phone_total'].values[0])
    distance = float(df_survey_nim['distance'].values[0])
    mode_transportation = df_survey_nim['mode_transportation'].values[0]

    df_dates = df_schedule_nim.groupby(['date'])[['emission', 'electricity', 'paper', 'classroom']].sum().reset_index()
    df_dates.rename(columns={'emission': 'courses_emission'}, inplace=True)

    df_dates['online_day'] = True
    df_dates['commuting_emission'] = 0
    df_dates['outclass_emission'] = 0

    for index, row in df_dates.iterrows():
      date = row['date']

      # Create temporary dataframe called df_temp
      df_temp = df_schedule_nim[df_schedule_nim['date'] == date][['date', 'start_time', 'end_time', 'is_online']].copy()

      # Convert time strings to datetime objects
      df_temp['start_time'] = pd.to_datetime(df_temp['start_time'], format='%H:%M')
      df_temp['end_time'] = pd.to_datetime(df_temp['end_time'], format='%H:%M')

      # Sort the dataframe by start_time
      df_temp.sort_values(by='start_time', inplace=True)

      online_day = (False if "Tatap Muka" in df_temp["is_online"].values else True) or online_method
      if (online_day):
        # print("Online..")
        smartphone_emission = electronic_emission(smartphone_power, pandemic_day_phone_total)
        laptop_emission = electronic_emission(laptop_power, pandemic_day_laptop_outclass)
        ac_emission = electronic_emission(ac_power, pandemic_day_laptop_total * frequency[pandemic_AC_frequent])
        outclass_emission = smartphone_emission + laptop_emission + ac_emission
        df_dates.at[index, 'outclass_emission'] = outclass_emission

      else:
        # print("Offline..")
        # Calculate how many commuting in a day
        counter = commuting_counter(df_temp, date)
        commuting_emission = commuting_emission_calculation(distance, mode_transportation, counter)
        df_dates.at[index, 'commuting_emission'] = commuting_emission

        smartphone_emission = electronic_emission(smartphone_power, day_phone_total)
        laptop_emission = electronic_emission(laptop_power, day_laptop_outclass)
        # STILL ON DEBATE
        ac_emission = electronic_emission(ac_power, day_laptop_total * frequency[pandemic_AC_frequent])
        outclass_emission = smartphone_emission + laptop_emission + ac_emission
        df_dates.at[index, 'outclass_emission'] = outclass_emission

      df_dates.at[index, 'online_day'] = online_day

    df_dates['total_emission'] = df_dates['courses_emission'] + df_dates['commuting_emission'] + df_dates['outclass_emission']
    return df_dates

def student_calculation(NIM, start_date, end_date, online_method=False):
    # Filter participants dataframe by NIM, Year, and Semester
    date1 = get_year_semester(start_date)
    date2 = get_year_semester(end_date)
    df_participants_nim = df_participants[(df_participants['NIM'] == NIM) &
     ((df_participants['year'] > date1['year']) | ((df_participants['year'] == date1['year']) & (df_participants['semester'] >= date1['semester']))) &
     ((df_participants['year'] < date2['year']) | ((df_participants['year'] == date2['year']) & (df_participants['semester'] <= date2['semester'])))].copy()
    
    df_participants_nim['kode_kelas'] = df_participants_nim['year'].astype(str) + "-" + df_participants_nim['semester'].astype(str) + "-" + df_participants_nim['course_id'] + "-" + df_participants_nim['class_number'].astype(str)

    # Filter schedule dataframe by Date
    df_schedule_nim = df_schedule[(df_schedule['date'] >= start_date) &
                                  (df_schedule['date'] <= end_date) &
                                  (df_schedule['key'].isin(df_participants_nim['kode_kelas']))].copy()
    df_schedule_nim = pd.merge(df_schedule_nim, df_class_count[['key', 'counts']], on ='key')

    # Combine course schedule with practicum schedule
    df_practicum_nim = df_practicum[(df_practicum['date'] >= start_date) & (df_practicum['date'] <= end_date)].copy()
    df_practicum_nim = df_practicum.merge(df_participants_nim[['year', 'semester', 'course_id']], on=['year', 'semester', 'course_id'], how='inner')
    df_schedule_nim = pd.concat([df_schedule_nim, df_practicum_nim])
    df_schedule_nim = df_schedule_nim.sort_values(['date', 'start_time'], ascending = [True, True], ignore_index=True)

    # Retrieve the student learning behavior profile
    df_survey_nim = df_survey[df_survey['NIM'] == NIM].copy()

    # Phase 1: Courses Schedule Emission
    df_schedule_nim = courses_schedule_calculation(df_schedule_nim, df_survey_nim, online_method)

    # Phase 2: Emission in a Day
    df_dates = day_calculation(df_schedule_nim, df_survey_nim, online_method)

    return df_schedule_nim, df_dates

def category_distribution(df_dates):
  return {
      "electricity": float(df_dates['electricity'].sum() + df_dates['outclass_emission'].sum()),  
      "commuting": float(df_dates['commuting_emission'].sum()),
      "paper": float(df_dates['paper'].sum()),
      "classroom": float(df_dates['classroom'].sum())
  }

def in_class_out_class(df_dates):
  return {
      "out_class": float(df_dates['outclass_emission'].sum() + df_dates['commuting_emission'].sum()),  
      "in_class": float(df_dates['courses_emission'].sum())
  }

def activity_distribution(df_dates, df_schedule_nim):
  # Pivot the dataframe
  pivot_df = df_schedule_nim.pivot_table(
      index='date',
      values='emission',
      columns='activity',
      aggfunc='sum'
  )

  # Flatten the column names
  pivot_df = pivot_df.fillna(0)
  df_activity = pivot_df.sum()

  return {
      "coursework": float(df_dates['outclass_emission'].sum()),  
      "commuting": float(df_dates['commuting_emission'].sum()),
      "exam": float(df_activity.get('UTS', 0) + df_activity.get('UAS', 0)),
      "lecture": float(df_activity.get('Kuis', 0) + df_activity.get('Kuliah', 0)),
      "practicum": float(df_activity.get('Praktikum', 0))
  }

if __name__ == '__main__':
    # Query
    NIM = 13520115
    start_date = "2021-08-23"
    end_date = "2023-04-20"

    print("NIM:", NIM)
    print("Start Date:", start_date)
    print("End Date:", end_date)

    # student_calculation(NIM, start_date, end_date)
    df_schedule_nim, df_dates = student_calculation(NIM, start_date, end_date)
    print(df_schedule_nim.tail(5))
    print(df_dates.tail(5))
    print(category_distribution(df_dates))
    print(in_class_out_class(df_dates))
    print(activity_distribution(df_dates, df_schedule_nim))