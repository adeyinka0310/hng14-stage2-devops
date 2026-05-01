# FIXES.md — Bug Documentation

## Overview
All bugs found in the starter repository and how they were fixed.

---

## Bug #1 — API hardcoded Redis host
- **File:** `api/main.py`
- **Line:** ~10
- **Problem:** Redis connection used `host="localhost"`. In Docker, services
  communicate by service name (e.g., `redis`), not `localhost`. This caused
  the API to crash on startup inside containers.
- **Fix:** Changed to read `REDIS_HOST` from environment variable:
  `REDIS_HOST = os.environ.get("REDIS_HOST", "redis")`

---

## Bug #2 — Redis missing `decode_responses=True`
- **File:** `api/main.py`, `worker/worker.py`
- **Line:** Redis client initialization
- **Problem:** Without `decode_responses=True`, Redis returns raw `bytes`
  objects instead of Python strings. `json.loads()` on bytes fails in
  Python 3.
- **Fix:** Added `decode_responses=True` to all `redis.Redis()` calls.

---

## Bug #3 — No CORS middleware on API
- **File:** `api/main.py`
- **Line:** Top of file
- **Problem:** The frontend runs on port 3000 and the API on port 8000.
  Browsers block "cross-origin" requests unless the server explicitly allows
  them via CORS headers. Without this, the frontend couldn't call the API.
- **Fix:** Added `CORSMiddleware` from `fastapi.middleware.cors`.

---

## Bug #4 — Worker used `rpop` instead of `brpop`
- **File:** `worker/worker.py`
- **Line:** Main loop
- **Problem:** `rpop` returns `None` immediately when the queue is empty,
  so the worker spun in a tight loop consuming 100% CPU doing nothing.
- **Fix:** Changed to `brpop` with `timeout=5`, which blocks (sleeps)
  until a job appears, using zero CPU while idle.

---

## Bug #5 — Worker didn't retry on startup
- **File:** `worker/worker.py`
- **Line:** Start of `main()`
- **Problem:** If Redis wasn't ready when the worker started, it crashed
  immediately with a connection error instead of waiting and retrying.
- **Fix:** Added a retry loop that pings Redis until it responds before
  entering the main processing loop.

---

## Bug #6 — Frontend listened on 127.0.0.1
- **File:** `frontend/server.js`
- **Line:** `app.listen()`
- **Problem:** `127.0.0.1` (loopback) only accepts connections from inside
  the same container. Docker routes traffic to `0.0.0.0`. Nothing could
  reach the frontend from outside the container.
- **Fix:** Changed to `app.listen(PORT, '0.0.0.0', ...)`

---

## Bug #7 — Frontend hardcoded API URL
- **File:** `frontend/server.js`
- **Line:** API URL constant
- **Problem:** URL was `http://localhost:8000`. In Docker, the API service
  name is `api`, not `localhost`.
- **Fix:** `const API_URL = process.env.API_URL || 'http://api:8000'`

---

## Bug #8 — No JSON body parsing in Express
- **File:** `frontend/server.js`
- **Line:** Middleware setup
- **Problem:** `express.json()` middleware was missing. Without it,
  `req.body` is always `undefined` when the client POSTs JSON data.
- **Fix:** Added `app.use(express.json())` before route handlers.

---

## Bug #9 — No /health endpoints
- **File:** `api/main.py`, `frontend/server.js`
- **Problem:** Docker HEALTHCHECK instructions need an HTTP endpoint to
  call. Without `/health` routes, containers can never become "healthy"
  and dependent services never start.
- **Fix:** Added `GET /health` endpoints to both services.

---

## Bug #10 — No PORT environment variable in frontend
- **File:** `frontend/server.js`
- **Problem:** Port was hardcoded as `3000`. Best practice (and required
  for docker-compose) is to read from `process.env.PORT`.
- **Fix:** `const PORT = process.env.PORT || 3000`