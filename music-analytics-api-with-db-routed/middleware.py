"""Middleware for Music Analytics API."""

from flask import request, g
from app import app
import time


@app.before_request
def log_request_start():
    """Log request start time for performance tracking."""
    g.start_time = time.time()


@app.after_request
def log_request_end(response):
    """Log request completion with timing."""
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        print(f"[{request.method}] {request.path} - {elapsed:.3f}s")
    return response
