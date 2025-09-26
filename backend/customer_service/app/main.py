import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# Read from env (set in docker-compose.yml). Fallback uses the Docker service name, NOT localhost.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@customer_db:5432/customers"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    """Smoke check used by compose/K8s. Returns ok only if DB is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "service": "customer"}
    except OperationalError:
        return {"status": "db connection failed", "service": "customer"}

@app.get("/")
def root():
    return {"message": "Customer service running"}
