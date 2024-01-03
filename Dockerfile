FROM python:3.9.18-alpine3.19 as base
LABEL author="karthikerathore@gmail.com"

WORKDIR /home

RUN pip3 install --upgrade pip

RUN pip3 install gunicorn
RUN pip3 install flask-restful
RUN pip3 install Flask
RUN pip3 install pyjwt
RUN pip3 install SQLAlchemy
RUN pip3 install Flask-SQLAlchemy
RUN pip3 install psycopg2-binary


COPY ./apps /home/apps/

CMD gunicorn -w 4 -b 0.0.0.0 'apps.app:create_app()'

