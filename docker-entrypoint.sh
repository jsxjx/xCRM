/code/manage.py syncdb --noinput
/usr/local/bin/gunicorn crm_site.wsgi:application -w 2 -b :8000
