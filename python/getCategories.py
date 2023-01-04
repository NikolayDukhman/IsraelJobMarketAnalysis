# We'll obtain the data by scraping one of the largest Israeli job portals drushim.co.il
# The vacancies divided by categories and sub-categories. We want first to obtain links to the categories and sub-categories as well. We'll store this data into CSV files

#Getting list of categories and subcategories in csv format
from bs4 import BeautifulSoup
import requests
# Fetch the page
r = requests.get("https://www.drushim.co.il/categories.aspx")
# Parse the HTML
soup = BeautifulSoup(r.content, "html.parser")
# Find all main categories
categories = soup.find_all("div", {"class": "flex cat-list"})
# Open the main categories CSV file for writing
subcategory_id=0
with open("subcategories.csv", "w") as csv_file2: 
  csv_file2.write(f"{'subcategory_id'},{'subcategory_name'}, {'subcat_internal_id'}, {'subcat_category_id'}, {'subcategory_link'}\n")
with open("main_categories.csv", "w") as csv_file:
  csv_file.write(f"{'category_id'},{'category_name'}, {'cat_internal_id'}, {'category_link'}\n")
  for idc, category in enumerate(categories):
    # Extract the category ID, name, and link
    category_id = idc+1
    cat_internal_id = category["catcode"]
    category_name = category["catname"]
    category_link = "https://www.drushim.co.il/jobs/cat"+cat_internal_id+"/"    
    # Write the category to the CSV file
    csv_file.write(f"{category_id},{category_name}, {cat_internal_id}, {category_link}\n")
    subcategories = category.find_all("a", {"class": "black--text display-14 no-underline mr-1 cat-list-item"})
    with open("subcategories.csv", "a") as csv_file2:  
      for subcategory in subcategories:
        subcategory_id = subcategory_id + 1 
        subcategory_name = subcategory.text.replace(",", "|")
        subcat_internal_id = subcategory["href"].split("/")[3]
        subcat_category_id = category_id
        subcategory_link = "https://www.drushim.co.il" + subcategory["href"]              
        csv_file2.write(f"{subcategory_id},{subcategory_name}, {subcat_internal_id}, {subcat_category_id}, {subcategory_link}\n")
