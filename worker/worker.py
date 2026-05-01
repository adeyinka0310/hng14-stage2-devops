import os
import json
import time
import logging
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BUG FIX: Original hardcoded "localhost" — must use service name in Docker
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

def get_redis():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True  # BUG FIX: Without this, bytes are returned, not strings
    )

def process_job(r, job_id):
    """Pick up a job and mark it as completed"""
    job_data = r.get(f"job:{job_id}")
    if not job_data:
        logger.warning(f"Job {job_id} not found in Redis")
        return

    job = json.loads(job_data)
    logger.info(f"Processing job {job_id} with payload: {job['payload']}")

    # Update status to processing
    job["status"] = "processing"
    r.set(f"job:{job_id}", json.dumps(job))

    # Simulate actual work (replace with real logic)
    time.sleep(2)

    # Mark as completed
    job["status"] = "completed"
    r.set(f"job:{job_id}", json.dumps(job))
    logger.info(f"Job {job_id} completed")

def main():
    """Main loop — keeps running and processing jobs"""
    logger.info(f"Worker starting, connecting to Redis at {REDIS_HOST}:{REDIS_PORT}")

    # BUG FIX: Original didn't retry on startup — if Redis wasn't ready, worker crashed
    # This loop retries until Redis is available
    while True:
        try:
            r = get_redis()
            r.ping()
            logger.info("Connected to Redis successfully")
            break
        except Exception as e:
            logger.warning(f"Redis not ready: {e}. Retrying in 2s...")
            time.sleep(2)

    logger.info("Worker is now listening for jobs...")
    while True:
        try:
            # brpop BLOCKS and waits — it sleeps until a job arrives (efficient!)
            # BUG FIX: Original used rpop which busy-loops using 100% CPU
            result = r.brpop("job_queue", timeout=5)
            if result:
                _, job_id = result
                process_job(r, job_id)
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection lost: {e}. Reconnecting...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()