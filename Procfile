release: python manage.py migrate --chdir core
web: gunicorn core.wsgi:application --chdir core --log-file -