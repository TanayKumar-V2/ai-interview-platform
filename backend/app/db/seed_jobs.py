from app.db.database import SessionLocal
from app.models.job_posting import JobPosting

SAMPLE_JOBS = [
    {
        "title": "Backend Engineer",
        "company": "Nimbus Systems",
        "description": "We are looking for a backend engineer experienced in Python, FastAPI, and PostgreSQL to build scalable APIs for our SaaS platform. You will work closely with the product team to design robust data models and RESTful services.",
        "requirements": "Python, FastAPI or Django, PostgreSQL, REST API design, Docker",
        "location": "Remote",
    },
    {
        "title": "Frontend Developer",
        "company": "Brightloop Media",
        "description": "Join our team to build responsive, accessible web interfaces using React and TypeScript. You'll collaborate with designers to translate Figma mockups into pixel-perfect, performant components.",
        "requirements": "React, TypeScript, Tailwind CSS, REST/GraphQL integration",
        "location": "Bangalore, India",
    },
    {
        "title": "Data Analyst",
        "company": "Verawave Analytics",
        "description": "Analyze large datasets to extract actionable business insights. Build dashboards and reports using SQL and Python, and present findings to stakeholders across the organization.",
        "requirements": "SQL, Python, Pandas, data visualization tools like Tableau or PowerBI",
        "location": "Remote",
    },
    {
        "title": "Machine Learning Engineer",
        "company": "Quanta Labs",
        "description": "Design and deploy machine learning models for production use cases including recommendation systems and natural language processing. Strong emphasis on MLOps and model monitoring.",
        "requirements": "Python, PyTorch or TensorFlow, MLOps, cloud deployment (AWS/GCP)",
        "location": "Hyderabad, India",
    },
    {
        "title": "DevOps Engineer",
        "company": "Ironclad Cloud",
        "description": "Own our CI/CD pipelines and infrastructure automation. Manage containerized deployments and improve system reliability across staging and production environments.",
        "requirements": "Docker, Kubernetes, CI/CD tools, Terraform, AWS",
        "location": "Remote",
    },
]


def seed_jobs():
    db = SessionLocal()
    try:
        existing_count = db.query(JobPosting).count()
        if existing_count > 0:
            print(f"Skipping seed: {existing_count} job postings already exist.")
            return

        for job_data in SAMPLE_JOBS:
            job = JobPosting(**job_data)
            db.add(job)

        db.commit()
        print(f"Seeded {len(SAMPLE_JOBS)} job postings.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_jobs()