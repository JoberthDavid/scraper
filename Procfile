web: python manage.py collectstatic --noinput && gunicorn scraper.wsgi --log-file -
celery: celery -A scraper worker --loglevel=info --concurrency=2