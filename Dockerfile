FROM python:3.12-slim as base
LABEL author="<karthikerathore@gmail.com>"

WORKDIR /home

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libncursesw5-dev openssl netcat-traditional \
    libssl-dev libsqlite3-dev tk-dev libgdbm-dev \
    libc6-dev libbz2-dev libffi-dev python3-dev python3-pip \
    libxml2-dev libxslt1-dev zlib1g zlib1g-dev python3-lxml \
    && rm -rf /var/lib/apt/lists/*


COPY ./requirements.docker.txt  /requirements.docker.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.docker.txt

COPY ./apps /home/apps/
COPY ./wait-for.sh /home/
COPY ./docker_env.sh /home/

RUN chmod 777 docker_env.sh

COPY wsgi.py /home/
COPY uwsgi.ini /uwsgi.ini

CMD sh ./wait-for.sh notes-db:5432 -- echo "postgres is up!" && \
    . ./docker_env.sh && uwsgi --ini /uwsgi.ini


