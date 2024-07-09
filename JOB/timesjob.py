"""
This module scrapes job listings from TimesJobs and saves the data to an Excel file and a database.
"""

import os
import datetime
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Base URL for job listings on TimesJobs with a placeholder for the page number
BASE_URL = ('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch'
            '&from=submit&txtKeywords=&txtLocation=India&sequence={}')

def fetch_job_data(page):
    """
    Fetch job data from the specified page.
    Parameters:
        page (int): The page number to fetch job data from.
    Returns:
        list: A list of dictionaries containing job details.
    """    
    url = BASE_URL.format(page)
    job_data = []
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print(f"Error fetching page {page}: {err}")
        return job_data

    soup = BeautifulSoup(response.text, 'html.parser')
    result = soup.find('ul', class_='new-joblist')

    if result:
        job_listings = result.find_all('li', class_='clearfix job-bx wht-shd-bx')

        for job in job_listings:
            try:
                title = job.find('a').text.strip()
                skill = job.find('span', class_='srp-skills').text.strip()
                description = job.find('label').next_sibling.strip()
                company_info = job.find('h3', class_='joblist-comp-name').text.strip().split('\n')
                company = company_info[0].strip()
                exp = job.find('ul', class_='top-jd-dtl clearfix').li.text.strip().split()[0]
                city = job.find('ul', class_='top-jd-dtl clearfix').span.text.strip()
                date_posted = job.find('span', class_='sim-posted').text.strip()
                job_url = job.find('a')['href']
                salary_tag = job.find('i', class_="material-icons rupee")
                salary = salary_tag.next_sibling.strip() if salary_tag else 'Not Mentioned'

                job_data.append({
                    'Job Title': title,
                    'Skill': skill,
                    'Description': description,
                    'Experience Reqd': exp,
                    'Company': company,
                    'City': city,
                    'Salary Range': salary,
                    'Date Posted': date_posted,
                    'URL': job_url
                })
            except (AttributeError, KeyError) as err:
                print(f"Error processing job listing: {err}")

    return job_data

def main():
    """
    Main function to scrape job listings from TimesJobs and save the data to an Excel file and a database.
    """
    job_data_list = []
    max_pages = 10

    for page in range(1, max_pages + 1):
        job_data_list.extend(fetch_job_data(page))
        print(f"Page {page} processed.")
        time.sleep(2)

    dff = pd.DataFrame(job_data_list)
    os.makedirs('data', exist_ok=True)
    file_path = os.path.join('data', f"TimesJobs_{str(datetime.date.today())}.xlsx")
    dff.to_excel(file_path, index=False)
    print(f"Data scraping completed and saved to Excel file: {file_path}")

    conn = sqlite3.connect("database.db")
    dff.to_sql("job", conn, if_exists="append", index=False)
    conn.close()
    print("Data saved to the database.")

if __name__ == "__main__":
    main()
