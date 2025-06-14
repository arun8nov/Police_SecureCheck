# Imporing Required Packages

import mysql.connector 
import pandas as pd 
import datetime
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
from sqlalchemy import create_engine 
import pymysql 

# Assign the database credentials and connect to the MySQL server
db_user = "root"
db_password = "admin"
db_host = "127.0.0.1"

# Connect to MySQL server and create a new database

mydb = mysql.connector.connect(
        host = db_host,
        user = db_user,
        password = db_password
    )
mycursor = mydb.cursor()

mycursor.execute("DROP DATABASE IF EXISTS police_secure_check;")
mycursor.execute("CREATE DATABASE police_secure_check;")
mycursor.execute("USE police_secure_check;")

# Read the data from Google Sheets using pandas

sheet_id = "16qEUKckLFy7j1qoSd1bSQURn9QXDb6ffSBAWzRkPsSg"
sheet_name = "Sheet1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(url)

# Concat stop_date and stop_time as one column
df["stop_date_time"] = df.stop_date + " "+ df.stop_time

# Change the datetime format 

df["stop_date_time"] = pd.to_datetime(df["stop_date_time"], format = "%Y-%m-%d %H:%M:%S")

# search_type column having null value also its not matnitory due to we having serach_conducted colum as bool type

# Filter out the required columns 

df = df[['stop_date_time','country_name', 'driver_gender',
        'driver_age', 'driver_race',  'violation', 'search_conducted', 'stop_outcome',
       'is_arrested', 'stop_duration', 'drugs_related_stop', 'vehicle_number']]

# Connect mysql server and insert the table into exsisting database

from sqlalchemy import create_engine 
import pymysql 

db_user = "root"
db_password = "admin"
db_host = "127.0.0.1"
db_name = "police_secure_check"

engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

with engine.begin() as connection:
    df.to_sql(name = "traffic_stop_police", con = connection, if_exists = 'replace', index = False)

print("Data added sucessfully")

