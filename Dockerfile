FROM daocloud.io/python:2.7
ADD requirements.txt /tmp/requirements.txt
RUN apt-get update
RUN apt-get install -y nginx vim
RUN pip install -r /tmp/requirements.txt
RUN mkdir /code
WORKDIR /code
COPY . /code
COPY docker-entrypoint.sh docker-entrypoint.sh
COPY nginx-web.conf /etc/nginx/nginx.conf
EXPOSE 8000
EXPOSE 80
RUN chmod +x docker-entrypoint.sh
CMD rm -f /etc/nginx/sites-enabled/default && ln -s /etc/nginx/sites-available/nginx-web.conf /etc/nginx/sites-enabled/default && service nginx start && /code/docker-entrypoint.sh
