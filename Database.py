import pandas as pd

DATA_PATH = "data/"
SURVEY_PATH = "01-survey.csv"
PARTICIPANTS_PATH = "02-participants.csv"
COURSES_PATH = "03-courses.csv"
CLASS_COUNT_PATH = "04-class-count.csv"
SCHEDULE_PATH = "05-schedule.csv"
PRACTICUM_PATH = "06-practicum.csv"
CLASSROOM_EF_PATH = "07-classroom-ef.csv"
ELECTRICITY_BILLS_PATH = "08-electricity-bills.csv"

class Database:
    def __init__(self):
        self.df_survey = pd.read_csv(DATA_PATH + SURVEY_PATH, index_col=0)
        self.df_participants = pd.read_csv(DATA_PATH + PARTICIPANTS_PATH, index_col=0)
        self.df_courses = pd.read_csv(DATA_PATH + COURSES_PATH, index_col=0)
        self.df_class_count = pd.read_csv(DATA_PATH + CLASS_COUNT_PATH, index_col=0)
        self.df_schedule = pd.read_csv(DATA_PATH + SCHEDULE_PATH, index_col=0)
        self.df_practicum = pd.read_csv(DATA_PATH + PRACTICUM_PATH, index_col=0)
        self.df_classroom_ef = pd.read_csv(DATA_PATH + CLASSROOM_EF_PATH, index_col=0)
        self.df_electricity_bills = pd.read_csv(DATA_PATH + ELECTRICITY_BILLS_PATH, index_col=0)

    def head(self, num):
        print(self.df_survey.head(num))
        print(self.df_participants.head(num))
        print(self.df_courses.head(num))
        print(self.df_class_count.head(num))
        print(self.df_schedule.head(num))
        print(self.df_practicum.head(num))
        print(self.df_classroom_ef.head(num))
        print(self.df_electricity_bills.head(num))
        
    
# Create an instance of the System class with the file paths to the dataframes
DB = Database()
DB.head(5)
