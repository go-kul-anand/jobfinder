DESCRIPTION
         JobFinder is a tool that gathers job listings from different websites into one place. It makes finding job opportunities easier by allowing users to search and filter jobs quickly. The tool provides a central point for accessing various job postings, saving time and effort.

TECHNOLOGIES USED

         FastAPI
         BeautifulSoup & Requests
         Selenium (Webdriver)
         SQLAlchemy
         SQLite
         Swagger UI
WEBSITES SCRAPPED
         
         NAUKRI
         Timesjob

Requirements:
      
        1.NAUKRI
                requests
                pandas
                numpy
                selenium
                bs4
                datetime
        2.TIMESJOB
                requests
                bs4
                pandas
                os
                datetime

 How JOBFINDER Works

        • Scrapes job listings from TimesJobs India, Naukri.
        • Parses job details such as title, skills, description, company, city, salary, and date posted.
        • Exports data to Database (SQLite)
        • FastAPI is used to create a web API quickly and efficiently, allowing users to interact with and retrieve data from a database via HTTP requests. 


                
                
