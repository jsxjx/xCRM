# Django 1.8
#/code/manage.py syncdb --noinput

# Django 1.9 since syncdb is deprecated
/code/manage.py makemigrations
/code/manage.py migrate
/usr/local/bin/gunicorn crm_site.wsgi:application -w 2 -b :8000
#python /code/manage.py runserver 0.0.0.0:8000