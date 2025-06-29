#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn elections.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 