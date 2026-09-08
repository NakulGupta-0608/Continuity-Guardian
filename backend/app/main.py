import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("continuity_guardian")

from backend.app.database.database import engine, Base, SessionLocal
import backend.app.database.models
from backend.app.data.demo_project import seed_demo_project
from backend.app.api.routers import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed demo dataset
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Checking and seeding 'Midnight at Platform 7' demo dataset...")
        seed_demo_project(db)
        logger.info("Demo dataset verified successfully.")
    except Exception as e:
        logger.error("Error during database seeding: %s", e)
    finally:
        db.close()
    
    yield
    logger.info("Shutting down Continuity Guardian backend.")

app = FastAPI(
    title="Continuity Guardian API",
    description="Autonomous Agentic AI Assistant for Filmmakers & Production Teams",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "name": "Continuity Guardian API",
        "tagline": "Your movie remembers. Your production doesn't have to.",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
