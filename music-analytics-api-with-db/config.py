"""Configuration settings for Music Analytics API."""
import os
from cachelib.file import FileSystemCache

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SESSION_TYPE = 'cachelib'
    SESSION_CACHELIB = FileSystemCache('/tmp/flask_session')
    SESSION_PERMANENT = False