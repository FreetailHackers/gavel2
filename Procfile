worker: PYTHONUNBUFFERED=true celery -A gavel:celery worker -E -P eventlet --loglevel=info
web: python initialize.py && gunicorn -k eventlet -b 0.0.0.0:8000 gavel:app --workers=3
