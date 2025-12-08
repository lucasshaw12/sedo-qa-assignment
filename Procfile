release: python manage.py migrate
web: gunicorn core.wsgi:application --chdir core --log-file -