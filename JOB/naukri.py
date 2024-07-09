"""
Scrapes job listings from Naukri.com using Selenium and BeautifulSoup,
saves data to an Excel file and a SQLite database.
"""

import os
import time
import datetime
import sqlite3
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
# Constants and configuration
CHROMEDRIVER_PATH = r'C:\webdriver\chromedriver.exe'
WINDOW_SIZE = "1920,1080"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

chrome_options = Options()
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
chrome_options.add_argument('--no-sandbox')

service = Service(CHROMEDRIVER_PATH)


def ensure_dir(directory):
    """
    Ensure the directory exists; create it if it does not.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def scrape_naukri_jobs():
    """
    Scrapes job listings from Naukri and saves the data to an Excel file and a database.
    """
    ensure_dir(OUTPUT_DIR)
    dff = pd.DataFrame(columns=[
        'Job Title', 'Skills', 'Description', 'Experience Reqd',
        'Company', 'City', 'Salary Range', 'Date Posted', 'URL'
    ])

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://www.naukri.com/jobs-in-india"
        driver.get(url)
        time.sleep(3)

        try:
            # Handling pop-up if it appears
            driver.find_element(
                By.XPATH,
                '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/p'
            ).click()
            driver.find_element(
                By.XPATH,
                '//*[@id="root"]/div[4]/div[1]/div/section[2]/div[1]/div[2]/span/span[2]/ul/li[2]'
            ).click()
        except NoSuchElementException as e:
            print(f"No pop-up to close or pop-up handling error: {e}")

        pages = range(1, 51)  # Adjust the range as needed

        for page in pages:
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            results = soup.find(id='listContainer')
            job_elems = results.find_all('div', class_='srp-jobtuple-wrapper')

            for job_elem in job_elems:
                title = job_elem.find('a', class_='title').text.strip()
                skills = ', '.join(
                    job_elem.find('ul', class_='tags-gt').text.strip().split()
                ) if job_elem.find('ul', class_='tags-gt') else 'Not-Mentioned'
                description = job_elem.find(
                    'span', class_='job-desc'
                ).text.strip() if job_elem.find('span', class_='job-desc') else 'Not-Mentioned'
                exp = job_elem.find(
                    'span', class_='expwdth'
                ).text.strip() if job_elem.find('span', class_='expwdth') else 'Not-Mentioned'
                company = job_elem.find('a', class_='comp-name').text.strip()
                city = job_elem.find(
                    'span', class_='locWdth'
                ).text.strip() if job_elem.find('span', class_='locWdth') else 'Not-Mentioned'
                salary = job_elem.find(
                    'span', class_='ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal'
                ).text.strip() if job_elem.find(
                    'span', class_='ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal'
                ) else 'Not-Mentioned'
                date = job_elem.find(
                    'span', class_='job-post-day'
                ).text.strip() if job_elem.find('span', class_='job-post-day') else 'Not-Mentioned'
                url = job_elem.find('a', class_='title')['href']
                dff = pd.concat(
                    [dff, pd.DataFrame([[title, skills, description, exp, company, city, salary, date, url]], columns=[
                        'Job Title', 'Skills', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range',
                        'Date Posted', 'URL'
                    ])],
                    ignore_index=True
                )
                print(f"Added job: {title}")

            try:
                driver.execute_script(
                    "window.scrollTo(0, (document.body.scrollHeight) - 1500)"
                )
                time.sleep(0.75)
                driver.find_element(
                    By.XPATH, '//*[@id="lastCompMark"]/a[2]/span'
                ).click()
                time.sleep(3)
            except NoSuchElementException as e:
                print(f"Error navigating to the next page: {e}")
                break

        try:
            current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(
                OUTPUT_DIR, f"NaukriJobListing_{current_time}.xlsx"
            )
            dff.to_excel(file_path, index=False)
            print(f"Saved all data to {file_path}")
        except PermissionError as e:
            print(f"Permission denied while saving file: {e}")
        except Exception as e:
            print(f"An error occurred while saving file: {e}")

        try:
            conn = sqlite3.connect("database.db")
            dff.to_sql("jobs", conn, if_exists="append", index=False)
            conn.close()
        except Exception as e:
            print(f"An error occurred while saving to database: {e}")

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        driver.quit()
        print("Scraping completed. Browser closed.")
if __name__ == "__main__":
    scrape_naukri_jobs()
