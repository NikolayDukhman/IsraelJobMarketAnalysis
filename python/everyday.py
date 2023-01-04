#We want to run this script daily with cron to check for updates
#strip text string of surrounding spaces and replace commas and quotes to avoid errors in CSV files 
def strip_replace(element,tag, selector):
    if(element.find(tag, selector)):
        return element.find(tag, selector).text.strip().replace(",", "|").replace("'", "").replace('"', "")
   
#reads job listing and returns string ready to be inserted to CSV file
def listing2list(job_listing):    
  title_class = "job-url primary--text font-weight-bold primary--text"
  name_class = "font-weight-bold bidi"
  description_class = "ma-0 display-18"
  requirements_class = "display-18 ma-0"
  salary_class = "layout display-18 pa-0 pa-0 wrap"
  subcat_class = "v-btn v-btn--contained v-btn--router theme--light v-size--default catBtn"
  profile_class = "no-underline-all"
  company_name = job_description = job_requirements = profile_link = salary = job_title = "unknown"
  details_list = []  

  for detail in job_listing.find_all("span", {"class": "display-18"}):
    detail2insert = detail.text.replace("|","").strip()
    if((detail2insert!="ועוד")and(detail2insert!="")): details_list.append(detail2insert)  
  company_location = details_list[0]
  experience_required = details_list[1]
  position_type = details_list[2]
  time_posted = calculate_date(details_list[3])
  #--------------------------------------------------------  
  if (job_listing.find("span", {"class": "font-weight-bold underline bidi"})): company_name = "hidden"       
  company_name = strip_replace(job_listing, "span", {"class": name_class})  
  job_title = strip_replace(job_listing, "span", {"class": title_class})
  job_description  = strip_replace(job_listing, "p", {"class": description_class})
  job_requirements = strip_replace(job_listing, "p", {"class": requirements_class})  
  salary = strip_replace(job_listing, "div", {"class": salary_class})  
       
  subcats = ""
  for link in job_listing.find_all("a"):
    if("/job/" in link['href']): listing_link = link['href']    
    if("דרושים" in link['href']):
      profile_link = link['href'].strip()
      if("https://www.drushim.co.il" in link['href']): profile_link = "/"+link['href'].split("/")[3].strip()+"/"
      if("," in link['href']): profile_link = "Comma error".strip()
    if("/jobs/subcat/" in link['href']): subcats = str(link['href'].split("/")[3]) + " " + subcats      
  return f"{category_id}, {listing_link}, {job_title}, {company_name}, {company_location},{profile_link},{experience_required}, {position_type}, {time_posted}, {job_description}, {job_requirements}, {salary}, {subcats}\n"

def load_category_page(category):
    start = time.time()    
    category_id = int(category.split("/")[4][3:])
    print("Reading category: " + str(category_id))
    driver.get(category) #Load category page    
    end = time.time()
    print("Category " + str(category_id) + " loaded in {:0.2f}".format(end - start) + " seconds")    
   
#When category page is loaded we can only see 25 first listings. We must click the "Show me more listings" button in order to load 10 more listings. We need to load all listings
def load_all_cat_listings(driver):    
  start = time.time() 
  try:
        num_listings=driver.find_element(By.XPATH,'//h6').text.split(" ")[1]
  except:
        num_listings = "All"    
  while True:
    try:      
      WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'הצג לי משרות נוספות')]"))).click()
    except TimeoutException:
      break
  end = time.time()
  print(str(num_listings) + " listings loaded in {:0.2f}".format(end - start) + " seconds")

#We have to expand listings in order to get all the data
def expand_all_listings(driver):
  start = time.time()
  listing_expand_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '+ לצפייה בפרטי המשרה')]")    
  for idx, listing_expand_element in enumerate(listing_expand_elements):
    try:
      webdriver.ActionChains(driver).click(listing_expand_element).perform()
    except:
      break
  end = time.time()    
  print("All listings clicked in {:0.2f}".format(end - start) + " seconds")
   
def calculate_date(posting_time):
  x = datetime.now().astimezone()
  if ("/" in posting_time): return posting_time
  if("שעות" in posting_time): hours_ago = int(posting_time.split(" ")[1])
  if("דקות" in posting_time): hours_ago = 1
  if(int(x.hour)-hours_ago>=0): return datetime.today().astimezone().strftime("%d/%m/%Y")
  else: return (datetime.today() - timedelta(days=1)).astimezone().strftime("%d/%m/%Y")  
   
#Headless Chromium. skipping images to save time and traffic
def driverWithOptions():  
  sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--disable-blink-features=AutomationControlled')
  prefs = {"profile.managed_default_content_settings.images": 2}
  options.add_experimental_option("prefs", prefs)
  return webdriver.Chrome('chromedriver',options=options)

#My processor has 4 cores, so I run 4 instances of this script simulateounesly with bash to save a lot of time. Bash file looks like this:
#!/bin/bash
#python everyday.py -c 0 &
#python everyday.py -c 1 &
#python everyday.py -c 2 &
#python everyday.py -c 3 &
#wait
#There are 32 categories and each batch contains 8 categories. Command line parameter is the batch number. By default (if no parameter is provided) all categories will be run in one thread.


def categories(batchNum):
    link_str = "https://www.drushim.co.il/jobs/cat"
    batch =[[],[],[],[],[]]
    batch[0] = [2,3,4,5,6,7,8,1]
    batch[1] = [9,10,11,12,13,14,15,16]
    batch[2] = [17,18,19,20,21,23,24,25]
    batch[3] = [27,28,29,30,31,32,33,26]
    batch[4] = batch[0] + batch[1] + batch[2] + batch[3]
    cat_list = []
    for el in batch[batchNum]:
      cat_list.append(link_str+str(el))
    return cat_list

#return categories that for some reason failed to load, so we can retry
def missing_categories(csv_path):
    directory = os.fsencode(csv_path)
    existing_cats = []    
    for file in os.listdir(directory):
         filename = os.fsdecode(file)
         if filename.endswith(".csv") and os.path.getsize(csv_path+filename)>20000: 
             existing_cats.append(filename.split("--")[0])
             continue
         else:
             continue                
    for x in existing_cats: 
        try:
            expected_cats.remove(x)
        except:
            continue
    categories=[]
    for x in expected_cats:   categories.append("https://www.drushim.co.il/jobs/cat"+x)   
    return categories
    
#imports
from datetime import datetime, timedelta
import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
import os
import sys
import pytz
from bs4 import BeautifulSoup
import requests
import argparse

#command line args
parser = argparse.ArgumentParser()
parser.add_argument(
        "-c",
        nargs="*",  # expects ≥ 0 arguments
        type=int,  
        default=[4],
)
args = vars(parser.parse_args())

process_start = time.time()
print("Starting data extraction process")
current_date = datetime.now(pytz.timezone('Israel')).strftime("%d-%m-%Y")
csv_path = "../../csv/daily/"
if not os.path.exists(csv_path + str(current_date)+"/upd"): os.makedirs(csv_path + str(current_date)+"/upd")
driver = driverWithOptions()
categories = categories(args["c"][0])

expected_cats = []
for cat in categories:  expected_cats.append(cat.split("/cat")[-1])
#-------------------
if(os.path.isfile('../../csv/updated/existing_listings_urls.csv')):
    existing_listings = pd.read_csv('../../csv/updated/existing_listings_urls.csv')
    existing_listings_df = existing_listings.iloc[:, 1]
    links_list = existing_listings_df.to_list()
else: links_list = []    
existing_urls = []
for link in links_list: existing_urls.append("https://www.drushim.co.il"+link.strip())
current_date = datetime.now(pytz.timezone('Israel')).strftime("%d-%m-%Y")
while(categories!=[]):
    categories = missing_categories(csv_path + str(current_date)+"/upd/")
    for category in categories:
            category_id = category.split("/")[4][3:]    
            load_category_page(category)      
            load_all_cat_listings(driver)  
            listing_expand_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '+ לצפייה בפרטי המשרה')]")
            listing_link_elements = driver.find_elements(By.XPATH,  "//a[@title='פתח משרה בחלון חדש']")
            #expand only the new listings 
            for listing_link_element, listing_expand_element in zip(listing_link_elements[::2],listing_expand_elements):          
                try:
                    if(listing_link_element.get_attribute('href') not in existing_urls): 
                        webdriver.ActionChains(driver).click(listing_expand_element).perform()
                except:
                    continue
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_listings = soup.find_all("div",{"class":"job-item-main"})
            cat_csv_path = csv_path + str(current_date)+"/upd/"+category_id+"--"+str(current_date) +".csv"
            with open(cat_csv_path, "w") as csv_file:
              csv_file.write(f"{'category_id'}, {'listing_link'},{'job_title'}, {'company_name'}, {'company_location'}, {'company_profile'}, {'experience_required'}, {'position_type'}, {'time_posted'}, {'job_description'}, {'job_requirements'},{'salary'}, {'subcategories_id'}\n")
              for job_listing in job_listings:
                csv_file.write(listing2list(job_listing))          
            print("Inserted listings successfully")   
driver.close()
