import pandas as pd
import joblib
import holidays

DATA_PATH = "data/"
SURVEY_PATH = "01-survey-full.csv"
PARTICIPANTS_PATH = "02-participants.csv"
COURSES_PATH = "03-courses.csv"
CLASS_COUNT_PATH = "04-class-count.csv"
SCHEDULE_PATH = "05-schedule.csv"
PRACTICUM_PATH = "06-practicum.csv"
CLASSROOM_EF_PATH = "07-classroom-ef.csv"
ELECTRICITY_BILLS_PATH = "08-electricity-bills.csv"
WEATHER_PATH = "09-weather.csv"
ITB_EMISSION_DATES = "full-version-emission-all-dates.csv"
ITB_EMISSION_SCHEDULES = "full-version-emission-all-schedules.csv"
ITB_EMISSION_PREDICTIVE = "emission-predictive-dataset.csv"

MODEL_PATH = "models/"
ITB_MODEL = "itb-predictive-model.joblib"
IF_MODEL = "if-predictive-model.joblib"
STI_MODEL = "sti-predictive-model.joblib"
MIF_MODEL = "mif-predictive-model.joblib"
 
class Database:
    def __init__(self):
        # LOAD DATABASE
        self.df_survey = pd.read_csv(DATA_PATH + SURVEY_PATH, index_col=0)
        self.df_participants = pd.read_csv(DATA_PATH + PARTICIPANTS_PATH, index_col=0)
        self.df_courses = pd.read_csv(DATA_PATH + COURSES_PATH)
        self.df_class_count = pd.read_csv(DATA_PATH + CLASS_COUNT_PATH, index_col=0)
        self.df_schedule = pd.read_csv(DATA_PATH + SCHEDULE_PATH, index_col=0)
        self.df_practicum = pd.read_csv(DATA_PATH + PRACTICUM_PATH, index_col=0)
        self.df_classroom_ef = pd.read_csv(DATA_PATH + CLASSROOM_EF_PATH, index_col=0)
        self.df_electricity_bills = pd.read_csv(DATA_PATH + ELECTRICITY_BILLS_PATH)
        self.df_electricity_bills['Date'] = pd.to_datetime(self.df_electricity_bills['Date'], format="%Y-%d-%m")
        self.df_electricity_bills['Date'] = self.df_electricity_bills['Date'].dt.strftime("%Y-%m-%d")
        self.df_weather = pd.read_csv(DATA_PATH + WEATHER_PATH)
        self.df_weather['date'] = pd.to_datetime(self.df_weather['date'])
        self.master_df_dates = pd.read_csv(DATA_PATH + ITB_EMISSION_DATES, index_col=0)
        self.master_df_schedules = pd.read_csv(DATA_PATH + ITB_EMISSION_SCHEDULES, index_col=0)
        self.df_predictive = pd.read_csv(DATA_PATH + ITB_EMISSION_PREDICTIVE, index_col=0)
        self.id_holidays = holidays.Indonesia()

        # MODEL LOAD
        self.itb_model = joblib.load(open(MODEL_PATH + ITB_MODEL, 'rb'))
        self.if_model = joblib.load(open(MODEL_PATH + IF_MODEL, 'rb'))
        self.sti_model = joblib.load(open(MODEL_PATH + STI_MODEL, 'rb'))
        self.mif_model = joblib.load(open(MODEL_PATH + MIF_MODEL, 'rb'))

    def head(self, num):
        print(self.df_survey.head(num))
        print(self.df_participants.head(num))
        print(self.df_courses.head(num))
        print(self.df_class_count.head(num))
        print(self.df_schedule.head(num))
        print(self.df_practicum.head(num))
        print(self.df_classroom_ef.head(num))
        print(self.df_electricity_bills.head(num))
        print(self.df_weather.head(num))

    def model_info(self):
        print("ITB model:", self.itb_model)
        print("IF model:", self.if_model)
        print("STI model:", self.sti_model)
        print("MIF model:", self.mif_model)
        
# Create an instance of the System class with the file paths to the dataframes
DB_INSTANCE = Database()
DB_INSTANCE.model_info()
