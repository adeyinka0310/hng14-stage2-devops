import os
import uuid
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis

# Set up logging so we can see what's happening in the container logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS allows the frontend (a different service) to talk to this API
# BUG FIX: Original had no CORS middleware, so frontend requests were blocked
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production you'd list specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read Redis connection details from environment variables
# BUG FIX: Original had hardcoded "localhost" which doesn't work in Docker
# In Docker, services talk to each other by SERVICE NAME, not localhost
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

def get_redis():
    """Create and return a Redis connection"""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True  # BUG FIX: Original missing this, caused bytes vs str errors
    )

class JobRequest(BaseModel):
    """This defines what a job submission looks like"""
    payload: str

@app.get("/health")
def health_check():
    """Health endpoint — Docker uses this to know if the API is alive"""
    try:
        r = get_redis()
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {str(e)}")

@app.post("/jobs")
def create_job(job_request: JobRequest):
    """Create a new job and push it to the Redis queue"""
    r = get_redis()
    job_id = str(uuid.uuid4())
    job_data = {
        "id": job_id,
        "payload": job_request.payload,
        "status": "pending"
    }
    # BUG FIX: Original used r.set() which doesn't allow the worker to pop jobs
    # We store the job details AND push the ID to a queue list
    r.set(f"job:{job_id}", json.dumps(job_data))
    r.lpush("job_queue", job_id)  # lpush adds to the LEFT of the queue list
    logger.info(f"Created job {job_id}")
    return {"job_id": job_id, "status": "pending"}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Get the current status of a job"""
    r = get_redis()
    job_data = r.get(f"job:{job_id}")
    # BUG FIX: Original didn't handle missing jobs, caused server crash
    if job_data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(job_data)