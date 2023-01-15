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
id=0
subcategory_id=0

with open("subcategories.csv", "w", encoding="utf-8") as csv_file2: 
  csv_file2.write(f"{'subcategory_id'},{'subcategory_name'}, {'subcat_internal_id'}, {'subcat_category_id'}, {'subcategory_link'}\n")
  csv_file2.close()
with open("main_categories.csv", "w", encoding="utf-8") as csv_file:
  csv_file.write(f"{'category_id'},{'category_name'}, {'cat_internal_id'}, {'category_link'}\n")
  for category in categories:
    id = id+1
    # Extract the category ID, name, and link
    category_id = id
    cat_internal_id = category["catcode"]
    category_name = category["catname"]
    category_link = "https://www.drushim.co.il/jobs/cat"+cat_internal_id+"/"    
    # Write the category to the CSV file
    csv_file.write(f"{category_id},{category_name}, {cat_internal_id}, {category_link}\n")

    subcategories = category.find_all("a", {"class": "black--text display-14 no-underline mr-1 cat-list-item"})
    with open("subcategories.csv", "a", encoding="utf-8") as csv_file2:  
      for subcategory in subcategories:
        subcategory_id = subcategory_id + 1 
        subcategory_name = subcategory.text
        subcat_internal_id = subcategory["href"].split("/")[3]
        subcat_category_id = id
        subcategory_link = "https://www.drushim.co.il" + subcategory["href"]              
        csv_file2.write(f"{subcategory_id},{subcategory_name}, {subcat_internal_id}, {subcat_category_id}, {subcategory_link}\n")  
csv_file.close()
