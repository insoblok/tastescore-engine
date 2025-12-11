import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from service.utils import logger
from routers import scan, sanctions, protocols
from service.scheduler import scheduler
from service.sanctions.ofac_ingester import OFACIngester

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    try:
        logger.info("Loading OFAC sanctions blacklist on startup...")
        ofac_ingester = OFACIngester()
        success = ofac_ingester.ingest()
        if success:
            logger.info("OFAC sanctions blacklist loaded successfully on startup")
        else:
            logger.warning("OFAC sanctions blacklist loading completed with warnings")
    except Exception as e:
        logger.error(f"Failed to load OFAC sanctions blacklist on startup: {e}")
        logger.info("Application will continue, but sanctions data may be incomplete")
    
    # Start scheduler for periodic updates
    scheduler.start()
    logger.info("Application started with scheduler")
    
    yield  # Application runs here
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Application shutting down")


app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI App"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(sanctions.router)
app.include_router(protocols.router)

@app.get("/api")
def read_root():
    logger.info("Root endpoint called")
    return {"message": f"Welcome to {app.title}"}