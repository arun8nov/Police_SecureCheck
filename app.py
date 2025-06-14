# Import required libraries

import mysql.connector
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import datetime
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")
import streamlit as st


# MySql Database Connection

db_user = "root"
db_password = "admin"
db_host = "127.0.0.1"
db_name = "police_secure_check" # Assigning DB Name

# Connect database

mydb = mysql.connector.connect(
        host = db_host,
        user = db_user,
        password = db_password
    )
mycursor = mydb.cursor()    

mycursor.execute(f"USE {db_name};")

# Function for Fetch query result from Database With Column Names As dataframe

def Query(Q):
    df = pd.read_sql(Q,mydb)
    return df

table = 'traffic_stop_police'

# Fetching data from the database table into a DataFrame

df = pd.DataFrame(Query(f'SELECT * FROM {table}'))

# Streamlit Visualization

# Setup layout & Title

st.set_page_config(page_title = "SecureCheck: Digital Ledger for Police Post Logs",
                   page_icon = "🚨",layout = "wide")
col1,col2 = st.columns([0.5,3])
col2.title("🚔SecureCheck: Digital Ledger for Police Post Logs🚔") # Title

col1.image("D:\Guvi\Projects\Project _1-SecureCheck Police\Sidebarlogo.jpg",width=200) # Logo image

st.divider()

# Home Layout Function

def Home():

    with st.expander("SecureCheck Data"):
        st.write("This is the data from the traffic stop police database. It contains information about traffic stops, including details about the driver, vehicle, and the outcome of the stop.")
        showData = st.multiselect("Select columns to display:",
                                options=df.columns.tolist(),
                                default=df.columns.tolist())
        st.dataframe(df[showData])

    Speeding_cases = df[df.violation == 'Speeding'].shape[0]
    Signal_cases = df[df.violation == 'Signal'].shape[0]
    Seatbelt_cases = df[df.violation == 'Seatbelt'].shape[0]
    DUI_cases = df[df.violation == 'DUI'].shape[0]
    Other_cases = df[df.violation == 'Other'].shape[0]


    total1,total2,total3,total4,total5 = st.columns(5,gap='small')

    with total1:
        st.info("Speeding_cases",icon='🚅')
        st.metric(label="Total Cases registed due to Speeding violation",value=f"{Speeding_cases}",border=True,)
    with total2:
        st.info("Signal_cases",icon='🚦')
        st.metric(label="Total Cases registed due to Signal violation",value=f"{Signal_cases}",border=True,)
    with total3:
        st.info("Seatbelt_cases",icon='💺')
        st.metric(label="Total Cases registed due to Seatbelt violation",value=f"{Seatbelt_cases}",border=True,)
    with total4:
        st.info("DUI_cases",icon='💊')
        st.metric(label="Total Cases registed due to DUI violation",value=f"{DUI_cases}",border=True,)
    with total5:
        st.info("Other_cases",icon='🅾')
        st.metric(label="Total Cases registed due to Other violation",value=f"{Other_cases}",border=True,)

# SQL Quary Function

def SQL_QUERY():
        
    st.title("SecureCheck : Query Box")

    Sql_dic = {
        '1.What are the top 10 vehicles involved in drug-related stops?' : f'SELECT vehicle_number,count(*) AS Freq_Arrest FROM {table} WHERE drugs_related_stop = True GROUP BY vehicle_number ORDER BY Freq_Arrest DESC LIMIT 10',
        '2. Which vehicles were most frequently searched?' : f'SELECT vehicle_number, count(*) AS Freq_Arrest FROM {table} WHERE drugs_related_stop = True GROUP BY vehicle_number ORDER BY Freq_Arrest DESC',
		
        '4. Which driver age group had the highest arrest rate?' : f'SELECT CASE WHEN driver_age < 18 THEN  \'UNDER AGE GROUP\' WHEN driver_age BETWEEN 18 AND 40  THEN  \'19 to 40 AGE GROUP\' WHEN driver_age BETWEEN 41 AND 60  THEN  \'41 to 60 AGE GROUP\' WHEN driver_age > 60  THEN  \'ABOVE 60 AGE GROUP\' END AS AGE_GROUP, COUNT(*) AS Case_count FROM {table} WHERE is_arrested = 1 GROUP BY AGE_GROUP ORDER BY Case_count DESC LIMIT 1',
        '5. What is the gender distribution of drivers stopped in each country?' : f'SELECT country_name,driver_gender,COUNT(*) FROM {table} GROUP BY  country_name,driver_gender ORDER BY country_name',
        '6. Which race and gender combination has the highest search rate?' : f'SELECT driver_race, driver_gender,ROUND(AVG(CASE WHEN search_conducted = 1 THEN 1.0 ELSE 0 END), 3) AS search_rate FROM {table} GROUP BY driver_race, driver_gender ORDER BY search_rate DESC LIMIT 1',
        '7. What time of day sees the most traffic stops?' : f'SELECT DATE_FORMAT(stop_date_time,\'%H %m %s\') AS Time,COUNT(*) AS Stop_frq FROM {table} GROUP BY Time',
        '8. What is the average stop duration for different violations?' : f'SELECT violation,stop_duration FROM {table} GROUP BY violation,stop_duration ORDER BY violation',
        '9. Are stops during the night more likely to lead to arrests?' : None,
        '10.Which violations are most associated with searches or arrests?' : f'SELECT violation,COUNT(*) AS Case_Count FROM {table} WHERE search_conducted = 1 AND is_arrested = 1 GROUP BY violation',
        '11.Which violations are most common among younger drivers (<25)?' : f'SELECT violation, count(*) AS Case_Count FROM f{table} WHERE driver_age <25 GROUP BY violation ORDER BY count(*) DESC',
        '12.Is there a violation that rarely results in search or arrest?' : f'SELECT violation, COUNT(*) AS count FROM {table} WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC;',
        '13.Which countries report the highest rate of drug-related stops?' : f'SELECT country_name,  COUNT(*) AS frq FROM {table} WHERE drugs_related_stop = TRUE GROUP BY country_name ORDER BY frq DESC',
        '14.What is the arrest rate by country and violation?' : f'SELECT country_name, violation,ROUND(AVG(CASE WHEN is_arrested = 1 THEN 1.0 ELSE 0 END), 3) AS arrest_rate FROM {table} GROUP BY country_name, violation ORDER BY arrest_rate DESC;',
        '15.Which country has the most stops with search conducted?' : f'SELECT country_name, COUNT(*) AS frq FROM {table} WHERE search_conducted = TRUE GROUP BY country_name ORDER BY frq DESC LIMIT 1',
        '16.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)' : f'SELECT DISTINCT country_name, EXTRACT(YEAR FROM stop_date_time) AS year, COUNT(*) OVER (PARTITION BY country_name, EXTRACT(YEAR FROM stop_date_time)) AS total_stops,SUM(is_arrested) OVER (PARTITION BY country_name, EXTRACT(YEAR FROM stop_date_time)) AS total_arrests FROM {table}',
        '17.Driver Violation Trends Based on Age and Race (Join with Subquery)' : f'SELECT driver_age, driver_race, violation, COUNT(*) AS count FROM {table} GROUP BY driver_age, driver_race, violation ORDER BY count DESC;',
        '18.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day' : f'SELECT EXTRACT(YEAR FROM stop_date_time) AS year, EXTRACT(MONTH FROM stop_date_time) AS month,  EXTRACT(HOUR FROM stop_date_time) AS hour, COUNT(*) AS total_stops FROM {table} GROUP BY year, month, hour ORDER BY year, month, hour;',
        '19.Violations with High Search and Arrest Rates (Window Function)' : f'SELECT DISTINCT violation,COUNT(*) OVER (PARTITION BY violation) AS total,SUM(search_conducted) OVER (PARTITION BY violation) AS total_searches,SUM(is_arrested) OVER (PARTITION BY violation) AS total_arrests FROM {table};',
        '20.Driver Demographics by Country (Age, Gender, and Race)' : f'SELECT country_name, driver_gender, driver_race,AVG(driver_age) AS avg_age, COUNT(*) AS count FROM {table} GROUP BY country_name, driver_gender, driver_race ORDER BY country_name',
        '21.Top 5 Violations with Highest Arrest Rates' : f'SELECT violation, count(*) AS Case_count FROM {table} WHERE is_arrested = 1 GROUP BY violation ORDER BY count(*) DESC'
        }

    with st.form(key = "Query Form"):
        A = st.selectbox("Select query:",Sql_dic.keys())


        query_button = st.form_submit_button(label = "Query")
        if query_button:
                st.write(A)
                st.write(Sql_dic[A])
                st.table(Query(Sql_dic[A]))

# New Data Input functipon

def Entry():
    
    form_values = {
        'stop_date' : None,
        'stop_time' : None,
        'country_name' : None, 
        'driver_gender' : None,
        'driver_race' : None,
        'driver_age' : None,  
        'violation' : None, 
        'search_conducted' : None, 
        'stop_outcome' : None,
        'is_arrested' : None, 
        'stop_duration' : None, 
        'drugs_related_stop' : None, 
        'vehicle_number' : None
    }

    # Streamlit Form for Data Entry
    ############# Form Layout #############

    st.title("SecureCheck : Form")

    with st.form(key = "Traffic Stop Form"):
        # Date and Time Input
        col1,col2 = st.columns(2)
        form_values['stop_date'] = col1.date_input("Enter Stop Date:")
        form_values['stop_time'] = col2.time_input("Enter Stop Time:")

        # Other Inputs
        form_values['country_name'] = st.text_input("Enter Country Name:")
        form_values['vehicle_number'] = st.text_input("Enter The Vechicle Number:")

        col3,col4,col5 = st.columns(3)
        form_values['driver_gender'] = col3.radio("Gender",["M","F"])
        form_values['driver_age'] = col4.number_input("Enter Driver Age:",min_value= 1,max_value=100)
        form_values['driver_race'] = col5.text_input("Enter Driver Race:")

        col6,col7,col8 = st.columns(3)
        form_values['violation'] = col6.selectbox("Enter Violation of the Driver:",
                                                ['Speeding', 'Other', 'DUI', 'Seatbelt', 'Signal'])
        form_values['stop_outcome'] = col7.selectbox("What is the Stop Outcome:",
                                                ['Ticket', 'Arrest', 'Warning'])
        form_values['stop_duration'] = col8.select_slider("Stop Duration:",
                                                        options=['16-30 Min', '0-15 Min', '30+ Min'])
        
        col9,col10,col11 = st.columns(3)
        form_values['search_conducted'] = col9.radio("Is Search Conducted:",
                                                        ['True','False'])
        form_values['is_arrested'] = col10.radio("Is Driver Arressted:",
                                                ['True','False'])
        form_values['drugs_related_stop'] = col11.radio("Is It Drug Related:",
                                                        ['True','False'])
        
        
        # Submit Button

        submit_button = st.form_submit_button(label = "Submit")
        if submit_button:
            if not all(form_values.values()):
                st.warning("Please fill out all fields")
            else:
                col11,col12 = st.columns(2)
                col11.write("#### Info")
                col11.table(form_values)
                col12.write("#### Summary")
                col12.write(f"🚗 A **{form_values['driver_age']}**-year-old **{form_values['driver_gender']}** driver was stopped for **{form_values['violation']}** at **{form_values['stop_time'].strftime("%I:%M %p")}**. **{print('search' if form_values['search_conducted'] == True else 'No search')}** was conducted, and he received a **{form_values['stop_outcome']}**. The stop lasted **{form_values['stop_duration']}** and was **{print('not drug-related' if form_values['drugs_related_stop'] == False else 'drug-related' )}**")    
                # Insert Data into Database
                Insert_button = st.form_submit_button(label='Insert Data into Database')
                if Insert_button: 
                    mydb.execute(f"USE {db_name};")     
                    mydb.execute(f"INSERT INTO {table} (stop_date_time,country_name,driver_gender ,driver_age, driver_race, violation ,search_conducted ,stop_outcome,is_arrested,stop_duration ,drugs_related_stop,vehicle_number) VALUES (\'{str(form_values['stop_date']) +' '+ str(form_values['stop_time'])}\',\'{form_values['country_name']}\',\'{form_values['driver_gender']}\',{form_values['driver_age']},\'{form_values['driver_race']}\',\'{form_values['violation']}\',{form_values['search_conducted']},\'{form_values['stop_outcome']}\',{form_values['is_arrested']},\'{form_values['stop_duration']}\',{form_values['drugs_related_stop']},\'{form_values['vehicle_number']}\')")
                    mydb.commit()
                    st.success("Data inserted successfully")
# Navigation
Home()
SQL_QUERY()
Entry()


