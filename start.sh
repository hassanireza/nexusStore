#!/bin/bash
echo "Starting NEXUS Store..."
cd "$(dirname "$0")"
python manage.py runserver 0.0.0.0:8000
