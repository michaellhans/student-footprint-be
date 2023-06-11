import pandas as pd

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
df_classroom_ef = pd.read_csv("data/07-classroom-ef.csv")
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
