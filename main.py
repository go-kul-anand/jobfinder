from fastapi import FastAPI, Query, HTTPException
import sqlite3
import traceback

# Initialize FastAPI app
app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

@app.get("/jobs/")
async def get_jobs(job_title: str = None, skills: str = None, company: str = None, city: str = None):
    try:
        # Base queries for naukri and timesjob tables
        naukri_query = "SELECT * FROM jobs WHERE 1=1"
        timesjob_query = "SELECT * FROM job WHERE 1=1"
        naukri_params = []
        timesjob_params = []

        # Ensure at least one filter is provided
        if job_title is None and skills is None and company is None and city is None:
            raise HTTPException(status_code=400, detail="At least one filter must be provided")

        # Add filters to naukri_jobs query
        if job_title is not None:
            naukri_query += " AND lower(`Job Title`) LIKE lower(?)"
            naukri_params.append('%' + job_title + '%')
        if skills is not None:
            naukri_query += " AND lower(Skills) LIKE lower(?)"
            naukri_params.append('%' + skills + '%')
        if company is not None:
            naukri_query += " AND lower(Company) LIKE lower(?)"
            naukri_params.append('%' + company + '%')
        if city is not None:
            naukri_query += " AND lower(City) LIKE lower(?)"
            naukri_params.append('%' + city + '%')

        # Add filters to timesjob_jobs query
        if job_title is not None:
            timesjob_query += " AND lower(`Job Title`) LIKE lower(?)"
            timesjob_params.append('%' + job_title + '%')
        if skills is not None:
            timesjob_query += " AND lower(Skills) LIKE lower(?)"
            timesjob_params.append('%' + skills + '%')
        if company is not None:
            timesjob_query += " AND lower(Company) LIKE lower(?)"
            timesjob_params.append('%' + company + '%')
        if city is not None:
            timesjob_query += " AND lower(City) LIKE lower(?)"
            timesjob_params.append('%' + city + '%')

        # Debug: Print the queries and parameters
        print("Naukri Query:", naukri_query)
        print("Naukri Params:", naukri_params)
        print("TimesJob Query:", timesjob_query)
        print("TimesJob Params:", timesjob_params)

        # Execute queries
        cursor.execute(naukri_query, naukri_params)
        naukri_jobs = cursor.fetchall()

        cursor.execute(timesjob_query, timesjob_params)
        timesjob_jobs = cursor.fetchall()

        # Combine results
        all_jobs = naukri_jobs + timesjob_jobs

        if not all_jobs:
            raise HTTPException(status_code=404, detail="Jobs not found")

        # Structure the response
        job_keys = ["index", "Job Title", "Skills", "Description", "Experience", "Company", "City", "Salary Range", "Date Posted", "URL"]
        jobs_response = [dict(zip(job_keys, job)) for job in all_jobs]

        return {"jobs": jobs_response}

    except Exception as e:
        print(f"Exception occurred: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Entry point to run the FastAPI application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
