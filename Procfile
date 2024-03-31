web: gunicorn scraper.wsgi --log-file -
celery: celery -A scraper worker --loglevel=info
celery: celery -A scraper worker -l info --concurrency 2