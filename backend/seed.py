from sqlalchemy.orm import Session

from models import Source

DEFAULT_SOURCES = [
    # Job boards
    {"label": "LinkedIn Jobs", "source_key": "linkedin", "category": "job_board", "enabled": True},
    {"label": "Indeed", "source_key": "indeed", "category": "job_board", "enabled": True},
    {"label": "Naukri", "source_key": "naukri", "category": "job_board", "enabled": True},
    {"label": "Google Jobs", "source_key": "google_jobs", "category": "job_board", "enabled": True},
    {"label": "Glassdoor", "source_key": "glassdoor", "category": "job_board", "enabled": False},
    {"label": "Wellfound", "source_key": "wellfound", "category": "job_board", "enabled": False},
    # Recruiter finders
    {"label": "Apollo.io", "source_key": "apollo", "category": "recruiter", "enabled": True},
    {"label": "Hunter.io", "source_key": "hunter", "category": "recruiter", "enabled": True},
    {"label": "Snov.io", "source_key": "snov", "category": "recruiter", "enabled": False},
]


def seed_sources(db: Session, user_id: int) -> None:
    if db.query(Source).filter(Source.user_id == user_id).first():
        return
    for s in DEFAULT_SOURCES:
        db.add(Source(user_id=user_id, is_custom=False, **s))
    db.commit()
