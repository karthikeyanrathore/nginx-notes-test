## Nginx Notes API's

Notes Restful API's hosted on nginx server.


## How to run application?

prerequisite: docker/ docker-compose
postgres container is acting weird, if you face any issue please write me karthikerathore@gmail.com
```bash
docker-compose down -v; docker-compose build;docker-compose up
```
See spec/openapi.yml to test all the API's locally.

## How to enter postgres container for debuggging?

```bash
docker exec -it notes-db psql -U postgres
```

## smol architecture

```mermaid
graph LR

client -->|"HTTP without SSL"| nginx-load-balancer:80 
nginx-load-balancer:80 --> |"HTTP" | notes-api_1:8000
nginx-load-balancer:80 --> |"HTTP" | notes-api_2:8000
nginx-load-balancer:80 --> |"HTTP" | notes-api_3:8000
nginx-load-balancer:80 --> |"HTTP" | notes-api_4:8000
nginx-load-balancer:80 --> |"HTTP" | notes-api_5:8000
nginx-load-balancer:80 --> |"HTTP" | notes-api_6:8000

notes-api_1:8000 --> |"DB connection" | notes-db:5432
notes-api_2:8000 --> |"DB connection" | notes-db:5432
notes-api_3:8000 --> |"DB connection" | notes-db:5432
notes-api_4:8000 --> |"DB connection" | notes-db:5432
notes-api_5:8000 --> |"DB connection" | notes-db:5432
notes-api_6:8000 --> |"DB connection" | notes-db:5432
```

## uWSGI architecture



Libraries used 
1. Flask-Restful lib
2. gunicorn
3. postgresQL
4. nginx
5. docker-compose


## core features
* added text search index for search notes
* added rate limiter for controlling API requests.
* disabled `TCP_NODELAY` option for performance.
