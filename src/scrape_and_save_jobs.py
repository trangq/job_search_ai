# scrape_jobs_to_csv.py

from jobspy import scrape_jobs
import pandas as pd
import os

WORK_DIR = "D:/job-search-ai"

def scrape_and_save_jobs(search_term="data scientist", location="HaNoi"):
    print("🔍 Đang scrape job từ nhiều nguồn...")
    job_data = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"],
        search_term=search_term,
        google_search_term=f"{search_term} jobs near {location} City",
        location=location,
        results_wanted=30,
        hours_old=72,
        country_indeed='Vietnam',
    )

    os.makedirs(WORK_DIR, exist_ok=True)
    output_path = os.path.join(WORK_DIR, "job_listings.csv")
    job_data.to_csv(output_path, index=False)
    print(f"✅ Đã lưu kết quả vào {output_path}")

if __name__ == "__main__":
    scrape_and_save_jobs()
        