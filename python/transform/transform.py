#Now when we have our data loaded into CSVs we want to transform it. At the end of the process I want to have several CSV files ready to be inseted into our database.
#But first... I noticed some job descriptions contain phone numbers and I want to extract the phones using regular expressions.
#We'll extract the numbers and insert them into a new column

#We start with making a pandas dataframe by uniting all job listings we got so far.

# df columns meaning for reference
#df[0] - Category           #df[1] - Job URL                #df[2] - Job title    #df[3] - Company name    #df[4] - Location    
#df[5] - Company URL        #df[6] - Experience required    #df[7] - Job type     #df[8] - Posting date    
#df[9] - Job description    #df[10] - Job requirements      #df[11] - Salary      #df[12] - Subcategories

import os
import glob
import pandas as pd
from datetime import datetime, timedelta
import pytz
import sys
import re
import numpy as np

current_date = datetime.now(pytz.timezone('Israel')).strftime("%d-%m-%Y")
os.chdir(sys.path[0]) #make sure we are in the current script directory
os.chdir("../../csv/daily/"+str(current_date)) # Change directory to where raw data from today is located
all_filenames = [i for i in glob.glob('*.{}'.format('csv'))]
df = pd.concat([pd.read_csv(f, header=None, skiprows=1) for f in all_filenames ]) # Create dataframe by uniting all csv files
df = df[(df[9]!=" None") & (df[10]!=" None") & (df[12]!="")].drop_duplicates(subset = [1]) #Filter out entries that are in the database already
df[8] = df[8].apply(lambda x:x.strip()) #there are unnecessary spaces in the date field which should be removed
df[13] = df[10].apply(lambda x:re.compile(".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?",re.S).findall(str(x)))#create column for the phones we extract from description (df[10])
os.chdir(sys.path[0])
csv_path = "../../csv/transformed/"
os.chdir(csv_path)
df.to_csv( "transformed.csv", header = False, index=False, encoding='utf-8-sig') #Save the dataframe to CSV file transformed.csv in the ../../csv/transformed/ folder
