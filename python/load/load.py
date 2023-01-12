def read_and_insert_sql(conn, cur, row, table_name, column_name, values):
    s=''
    for i in range(0,len(values)): s = s + ' %s'  #create string of %s, %s, %s, ... the length of row we want to insert    
    df = pd.read_sql(f'select * from "{table_name}"', conn) # Retrieve the data from the table    
    if (values[-1] not in df[column_name].to_list()):# Check if the last value in the list is not in the table
        cur.execute(f"INSERT INTO \"{table_name}\" VALUES (DEFAULT ,{s.strip().replace(' ',',')})", values)# Create the SQL query with the number of placeholders equal to the number of values
        df = pd.read_sql(f'select * from "{table_name}"', conn)
    return df.index[df[column_name]==values[-1]].to_list()[0]+1 # Return the index of the last value inserted, plus one

def getDateValues(input): #returns ID of the input date in dimDate table
    df_date =  pd.read_sql('select date_id, date from "dimDate"', conn)
    my_date = datetime.strptime(input,'%d/%m/%Y').date()
    if (my_date not in df_date['date'].to_list()):
        d = input.split("/") #Splitting date in format 15/01/2023. so d[0]= 15, d[1] = 1, d[2] = 2023
        if (d[2] == 2022): year_id = 1
        if (d[2] == 2023): year_id = 2 # ugh I know, I know...
        weekday_id = my_date.weekday()+1
        quarter_id = (d[1]-1)//3+1
        cur.execute(f"INSERT INTO \"dimDate\" VALUES (DEFAULT, %s ,%s, %s ,%s, %s ,%s);", (my_date,d[0],d[1],d[2],weekday_id,quarter_id))  
        df_date =  pd.read_sql('select date_id, date from "dimDate"', conn)
    return df_date.index[df_date['date']==my_date].to_list()[0]+1        
   
def row2db(row): #Insert rows of the dataframe to the database      
    loc_id = read_and_insert_sql(conn, cur, row, 'dimLocation', 'name', (row[4],))
    comp_id = read_and_insert_sql(conn, cur, row, 'dimCompany', 'url', (row[3],row[5]))
    exp_id = read_and_insert_sql(conn, cur, row, 'dimExperience', 'experience', (row[6],))
    type_id = read_and_insert_sql(conn, cur, row, 'dimPositionType', 'position_type', (row[7],))
    date_id = getDateValues(row[8])    
    df_listing = pd.read_sql('select link  from "listingFacts"', conn)  
    if (row[1] not in df_listing['link'].to_list()):
        cur.execute(f"INSERT INTO \"listingFacts\" VALUES (DEFAULT ,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (row[0], row[1], row[2], comp_id, exp_id, row[9],row[10],row[11],row[13],loc_id,type_id,date_id))
       
from datetime import datetime, timedelta
import psycopg2
import csv
from settings import db_server, db_name, db_password
import pandas as pd
import os
import sys

os.chdir(sys.path[0])
csv_path = "../../csv/transformed/"
os.chdir(csv_path)  #move to the folder with our transformed CSV file
df = pd.read_csv( "transformed.csv", header = None) #Read CSV to DataFrame
conn = psycopg2.connect(host=db_server, password=db_password, dbname=db_name) #Create connection to our database
cur = conn.cursor()
df.apply(row2db, axis = 1) #Insert entries to the database as defined in the row2db function
conn.commit()
cur.close()
conn.close()
