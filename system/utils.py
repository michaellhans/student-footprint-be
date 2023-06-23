from .database import DB_INSTANCE
import numpy as np
from datetime import datetime, timedelta

# 1. COMMUTING EMISSION CALCULATION
# Commuting Emission Factor
TRANSPORTATION_EF = {
  'Public transportation': 424.0,
  'Private car': 324.4897959183673,
  'Private motorcycle': 113.57142857142857,
  'Online transportation - car': 397.25,
  'Online transportation - motorcycle': 113.57142857142857,
  'Walk': 39,
  'Bicycle': 17,
}

# Calculate the commuting emission in kg CO2e
def commuting_emission_calculation(distance, mode_transportation, counter):
    return (distance * TRANSPORTATION_EF[mode_transportation] * (1 + counter) * 2) / 1000

# 2. ELECTRICITY EMISSION CALCULATION
# Frequent pattern
frequency = {
  "Never": 0,
  "Rarely": 0.25,
  "Sometimes": 0.5,
  "Often": 0.75,
  "Always": 1,
}

# Electronic Device Emission Factor
smartphone_capacity = 4500  # mAh
smartphone_volt = 3.7       # volt
smartphone_power = 16.65    # Wh
laptop_power = 38           # Wh
ac_power = 780              # Wh
hours_of_use = 5            # hours
electricity_ef = 0.804      # kWh

# Calculate the electronic usage in kWh
def electronic_emission(power, hours_of_use):
  kwh_consumed = power * hours_of_use / 1000.0
  return kwh_consumed * electricity_ef


# 3. CLASSROOM EMISSION CALCULATIOn
df_classroom_ef = DB_INSTANCE.df_classroom_ef
room = df_classroom_ef.set_index('Room')['EF'].to_dict()
room['-'] = room['7606']
room['7610'] = room['7609']
room['BSc'] = room['Multipurpose']

# Calculate the classroom emission in CO2e
def classroom_emission(location, hours_of_use):
  kwh_consumed = 0
  if location in room:
    kwh_consumed = room.get(location) * hours_of_use / 1000.0
  else:
    location = location.split(" ")[0]
    kwh_consumed = room.get(location, room['-']) * hours_of_use / 1000.0
  return kwh_consumed * electricity_ef

# 4. PAPER EMISSION CALCULATION
paper_ef = 2.958622
def paper_emission(num_of_paper):
  return num_of_paper / 500 * paper_ef

# Calculate MAPE
def mean_absolute_percentage_error(y_test, y_pred):
  y_test, y_pred = np.array(y_test), np.array(y_pred)
  return np.mean(np.abs((y_test - y_pred) / y_test)) * 100

def get_forecasting_date(start_date, end_date):
  # Convert the date strings to datetime objects
  start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
  end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

  # Calculate the delta days
  delta = end_date_obj - start_date_obj
  new_end_date_obj = end_date_obj + timedelta(days=delta.days)
  new_end_date = new_end_date_obj.strftime('%Y-%m-%d')
  print(new_end_date)
  print(end_date)

  return new_end_date

def debugging_api(entity, start_date, end_date):
    print(entity, end="; ")
    print("Start Date:", start_date, end="; ")
    print("End Date:", end_date)

def is_holiday(date):
    if date in DB_INSTANCE.id_holidays:
        return True
    else:
        return False

def is_pandemic(date):
  if (date.year < 2023):
    return True
  else:
    return False
  
code_mapping = {135: "IF", 182: "STI", 235: "MIF"}