import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import datetime
import time
import openpyxl
import sqlite3
# URL for job listings
base_url = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=&txtLocation=India&sequence={}'

def main():
    # DataFrame to store job listings
    dff = pd.DataFrame(columns=['Job Title','Skill', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])
    
    # Loop through pages
    page_counter = 0
    max_pages = 10  # Number of pages to scrape
    
    for page in range(1, max_pages + 1):
        url = base_url.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find job listings
        result = soup.find('ul', class_='new-joblist')
        if result:
            job_listings = result.find_all('li', class_='clearfix job-bx wht-shd-bx')
            
            for job in job_listings:
                try:
                    # Job Title
                    title = job.find('a').text.strip()



                    #JOB SKILL
                    skill = job.find('span', class_='srp-skills').text.strip()
                    
                    # Description
                    description = job.find('label').next_sibling.strip()
                    
                    # Company
                    company_text = job.find('h3', class_='joblist-comp-name').text.strip()
                    company = company_text.split('\n')[0].strip()
                    
                    # Experience
                    exp = job.find('ul', class_='top-jd-dtl clearfix').li.text.strip().split()[0]
                    
                    # City
                    city = job.find('ul', class_='top-jd-dtl clearfix').span.text.strip()
                    
                    # Date Posted
                    date_posted = job.find('span', class_='sim-posted').text.strip()
                    
                    # Job URL
                    job_url = job.find('a')['href']
                    
                    # Salary (if available)
                    salary_tag = job.find('i', class_="material-icons rupee")
                    salary = salary_tag.next_sibling.strip() if salary_tag else 'Not Mentioned'
                    
                    # Append data to DataFrame
                    dff = pd.concat([dff, pd.DataFrame([[title, skill, description, exp, company, city, salary, date_posted, job_url]], 
                                        columns=['Job Title', 'Skill', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])], 
                                        ignore_index=True)
                except Exception as e:
                    print(f"Error processing job listing: {e}")
                    
        print(f"Page {page} processed.")
        time.sleep(2)  # Sleep to mimic human browsing and avoid being blocked

    # Save DataFrame to Excel
    os.makedirs('data', exist_ok=True)
    dff.to_excel(os.path.join('data', f"TimesJobs_{str(datetime.date.today())}.xlsx"), index=False)
    print("Data scraping completed and saved to Excel file.")

    #SAve to DB
    conn= sqlite3.connect("database.db")
    dff.to_sql("job", conn, if_exists="append", index=True)
    conn.close()

if __name__ == "__main__":
    main()
