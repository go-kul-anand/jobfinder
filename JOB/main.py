"""
FastAPI application for fetching job listings from an SQLite database.
The app connects to a SQLite database and defines an endpoint to fetch jobs
based on various filters such as job title, skills, company, and city.
"""

import sqlite3
import traceback
from fastapi import FastAPI, HTTPException

# Initialize FastAPI app
app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

@app.get("/jobs/")
async def get_jobs(
    job_title: str = None,
    skills: str = None,
    company: str = None,
    city: str = None
):
    """
    Fetch job listings based on provided filters.
    Parameters:
        job_title (str): Filter by job title.
        skills (str): Filter by required skills.
        company (str): Filter by company name.
        city (str): Filter by job location (city).
    Returns:
        dict: A dictionary containing a list of filtered job listings.
    """
    try:
        naukri_query = "SELECT * FROM jobs WHERE 1=1"
        timesjob_query = "SELECT * FROM job WHERE 1=1"        
        naukri_params = []
        timesjob_params = []

        if job_title is None and skills is None and company is None and city is None:
            raise HTTPException(status_code=400, detail="At least one filter must be provided")

        if job_title is not None:
            naukri_query += " AND lower(`Job Title`) LIKE lower(?)"
            naukri_params.append(f'%{job_title}%')
            timesjob_query += " AND lower(`Job Title`) LIKE lower(?)"
            timesjob_params.append(f'%{job_title}%')
        if skills is not None:
            naukri_query += " AND lower(Skills) LIKE lower(?)"
            naukri_params.append(f'%{skills}%')
            timesjob_query += " AND lower(Skills) LIKE lower(?)"
            timesjob_params.append(f'%{skills}%')
        if company is not None:
            naukri_query += " AND lower(Company) LIKE lower(?)"
            naukri_params.append(f'%{company}%')
            timesjob_query += " AND lower(Company) LIKE lower(?)"
            timesjob_params.append(f'%{company}%')
        if city is not None:
            naukri_query += " AND lower(City) LIKE lower(?)"
            naukri_params.append(f'%{city}%')
            timesjob_query += " AND lower(City) LIKE lower(?)"
            timesjob_params.append(f'%{city}%')
        cursor.execute(naukri_query, naukri_params)
        naukri_jobs = cursor.fetchall()
        cursor.execute(timesjob_query, timesjob_params)
        timesjob_jobs = cursor.fetchall()
        all_jobs = naukri_jobs + timesjob_jobs
        if not all_jobs:
            raise HTTPException(status_code=404, detail="Jobs not found")
        job_keys = [
            "index", "Job Title", "Skills", "Description",
            "Experience", "Company", "City", "Salary Range",
            "Date Posted", "URL"
        ]
        jobs_response = [dict(zip(job_keys, job)) for job in all_jobs]
        return {"jobs": jobs_response}
    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) from e  # Modified line
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
