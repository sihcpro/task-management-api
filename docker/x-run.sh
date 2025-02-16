echo "$@"

cd /app && PYTHONPATH=. python manage.py collectstatic
cd /app && PYTHONPATH=. python manage.py migrate
cd /app && PYTHONPATH=. python manage.py createsuperuser --noinput --username admin --email admin@yopmail.com
cd /app && PYTHONPATH=. python manage.py runserver 0.0.0.0:"$1"
