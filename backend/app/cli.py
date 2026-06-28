from app.db.seed import seed_application, write_seed_files
from app.db.session import Base, SessionLocal, engine
from app.models import entities  # noqa: F401


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_application(db)
    write_seed_files()
    print("InsightAI seed data created.")


if __name__ == "__main__":
    seed()
