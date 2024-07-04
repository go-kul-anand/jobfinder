import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import datetime
import time

# URL for job listings
base_url = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=&txtLocation=India&sequence={}'

def parse_date(date_posted_text):
    now = datetime.datetime.now()
    date_posted = None
    
    if 'today' in date_posted_text or 'few hours ago' in date_posted_text:
        date_posted = now
    elif 'day' in date_posted_text:
        days_ago = int(date_posted_text.split()[0])
        date_posted = now - datetime.timedelta(days=days_ago)
    elif 'hour' in date_posted_text:
        hours_ago = int(date_posted_text.split()[0])
        date_posted = now - datetime.timedelta(hours=hours_ago)
    else:
        try:
            date_posted = datetime.datetime.strptime(date_posted_text, '%d %b').replace(year=now.year)
            if date_posted > now:
                date_posted = date_posted.replace(year=now.year - 1)
        except ValueError:
            print(f"Unable to parse date: {date_posted_text}")
    
    return date_posted

def main():
    # Desired skills to filter jobs
    desired_skills = ['Salesforce', 'Servicenow', 'SAP', 'Oracle']  # Modify as per your requirement
    
    # DataFrame to store job listings
    dff = pd.DataFrame(columns=['Job Title', 'Skill', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])
    
    # Loop through pages
    max_pages = 100  # Number of pages to scrape
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

                    # Job Skill
                    skill_text = job.find('span', class_='srp-skills').text.strip()
                    skills = [s.strip().lower() for s in skill_text.split(',')]  # Split and clean skills

                    # Filter by desired skills
                    if not any(ds.lower() in skills for ds in desired_skills):
                        continue  # Skip if none of the desired skills are in the job listing

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
                    date_posted_text = job.find('span', class_='sim-posted').text.strip().lower()
                    date_posted = parse_date(date_posted_text)
                    
                    # Filter for jobs posted within the last 7 days
                    if date_posted and (datetime.datetime.now() - date_posted).days > 7:
                        continue  # Skip if job is older than 7 days

                    # Job URL
                    job_url = job.find('a')['href']
                    
                    # Salary (if available)
                    salary_tag = job.find('i', class_="material-icons rupee")
                    salary = salary_tag.next_sibling.strip() if salary_tag else 'Not Mentioned'
                    
                    # Append data to DataFrame
                    dff = pd.concat([dff, pd.DataFrame([[title, skill_text, description, exp, company, city, salary, date_posted.strftime('%Y-%m-%d'), job_url]], 
                                        columns=['Job Title', 'Skill', 'Description', 'Experience Reqd', 'Company', 'City', 'Salary Range', 'Date Posted', 'URL'])], 
                                        ignore_index=True)
                except Exception as e:
                    print(f"Error processing job listing: {e}")
                    
        print(f"Page {page} processed.")
        time.sleep(2)  # Sleep to mimic human browsing and avoid being blocked

    # Save DataFrame to Excel with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('data', exist_ok=True)
    file_name = f"TimesJobs_{timestamp}.xlsx"
    dff.to_excel(os.path.join('data', file_name), index=False)
    print(f"Data scraping completed and saved to {file_name}.")

if __name__ == "__main__":
    main()
