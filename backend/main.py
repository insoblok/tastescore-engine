import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from service.utils import logger
from routers import scan

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI App"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
    
@app.get("/api")
def read_root():
    logger.info("Root endpoint called")
    return {"message": f"Welcome to {app.title}"}