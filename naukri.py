import requests
import time
import datetime
import os

import pandas as pd
import numpy as np

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

CHROMEDRIVER_PATH = r'C:\webdriver\chromedriver.exe'
WINDOW_SIZE = "1920,1080"
chrome_options = Options()

# chrome_options.add_argument("--headless")
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument('--no-sandbox')

service = Service(CHROMEDRIVER_PATH)

def main():
    # Define the list of desired skills
    desired_skills = ['Salesforce', 'Servicenow', 'SAP', 'Oracle']  # Modify as per your requirement

    dff = pd.DataFrame(columns=['Job Title', 'Skills', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://www.naukri.com/jobs-in-india"
    driver.get(url)

    time.sleep(3)
    try: 
        driver.find_element(By.XPATH, '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/p').click()
        driver.find_element(By.XPATH, '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/ul/li[2]').click()
    except Exception as e:
        pass

    pages = np.arange(1, 101)  # Limit to 100 pages
    job_count = 0  # Initialize job counter

    for page in pages:
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        results = soup.find(id='listContainer')
        job_elems = results.find_all('div', class_='srp-jobtuple-wrapper')

        for job_elem in job_elems:
            # Post Title
            T = job_elem.find('a', class_='title')
            Title = T.text

            # Skills
            try:
                sk = job_elem.find('ul', class_='tags-gt')
                Skills = ', '.join(sk.text.strip().split())  # Split and join skills with commas
            except Exception as e:
                Skills = 'Not-Mentioned'

            # Check if any desired skills are in the extracted skills
            if any(skill.lower() in Skills.lower() for skill in desired_skills):
                # Description
                try:
                    D = job_elem.find('span', class_='job-desc')
                    Description = D.text
                except Exception as e:
                    Description = None
                
                # Experience  
                E = job_elem.find('span', class_='expwdth')
                if E is None:
                    Exp = "Not-Mentioned"
                else:
                    Exp = E.text
                
                # Company
                C = job_elem.find('a', class_='comp-name')
                Company = C.text
                
                # City
                try:
                    C = job_elem.find('span', class_='locWdth')
                    City = C.text
                except Exception as e:
                    City = None

                # Salary Range
                try:
                    S = job_elem.find('span', 'ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal')
                    Salary = S.text
                    print("Salary: ", Salary)
                except Exception as e:
                    Salary = "Not-Mentioned"
                    print("Salary Not Found")

                # Date Posted
                D = job_elem.find('span', class_='job-post-day')
                try:
                    date_text = D.text.strip().lower()
                    if 'just now' in date_text:
                        Date = datetime.datetime.now()
                    elif 'day' in date_text or 'days' in date_text:
                        days_ago = int(date_text.split()[0])
                        Date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
                    else:
                        try:
                            Date = datetime.datetime.strptime(date_text, '%d %b %Y')
                        except ValueError:
                            Date = None
                except Exception as e:
                    Date = None

                # Filter jobs posted within the last 7 days
                if Date and (datetime.datetime.now() - Date).days > 7:
                    continue

                U = job_elem.find('a', class_='title').get('href')
                URL = U

                # Ensure Date is not None before formatting
                if Date is None:
                    Date_formatted = "Not-Mentioned"
                else:
                    Date_formatted = Date.strftime('%Y-%m-%d')

                dff = pd.concat([dff, pd.DataFrame([[Title, Skills, Description, Exp, Company, City, Salary, Date_formatted, URL]], columns=['Job Title', 'Skills', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])], ignore_index=True)
                print(dff)

                job_count += 1
                if job_count % 50 == 0:
                    print(f"Processed {job_count} jobs, taking a short break...")
                    time.sleep(5)  # Pause for 5 seconds every 50 job listings

        driver.execute_script("window.scrollTo(0, (document.body.scrollHeight) - 1500)")

        time.sleep(0.75)

        next_button = driver.find_element(By.XPATH, '//*[@id="lastCompMark"]/a[2]/span')
        if not next_button:
            break  # Stop if the next button is not found

        next_button.click()

        time.sleep(3)

    # Save the data to an Excel file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"NaukriJobListing_{timestamp}.xlsx"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    file_path = os.path.join(output_dir, file_name)
    dff.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")

    print("*********************CONCLUSION: FINISHED FETCHING DATA FROM NAUKRI.COM*********************")

    # Closing the Driver
    driver.close()

main()
