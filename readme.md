## Nginx Notes API's

Notes Restful API's hosted on nginx server.


## How to run application?

0. prerequisite: Docker/ Docker Compose version v2.24.0

If you face any issue please write me karthikerathore@gmail.com

1. run containers in production mode.
```bash
docker-compose down -v --remove-orphans; \
docker-compose --profile production build; \
docker-compose --profile production up;
```

2. run containers in develop mode.
```bash
docker-compose down -v --remove-orphans; \
docker-compose -f docker-compose-develop.yml down -v --remove-orphans; \
docker-compose -f docker-compose-develop.yml --profile develop build; \
docker-compose -f docker-compose-develop.yml --profile develop up;
```

3. clean up. run this if you are facing network <id> not found.
```bash
docker-compose down -v --remove-orphans; \
docker-compose -f docker-compose-develop.yml down -v --remove-orphans;
```

See spec/openapi.yml to test all the API's locally.

## How to develop app using [compose watch](https://docs.docker.com/compose/file-watch/#sync--restart)?
```bash
docker-compose -f docker-compose-develop.yml --profile develop  watch
```

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

```mermaid
graph LR

client -->|"http without SSL certs"| nginx-load-balancer:80 
nginx-load-balancer:80 --> |"HTTP/"| uWSGI-middleware:8000

subgraph uWSGI running in pre-fork mode
uWSGI-middleware:8000 --> |"starts"| master-process
master-process --> |"loads FLASK app"| notes-api:8000
master-process --> |"os.fork() / spin up 5 child processes"| workers-processes
worker-1 --> master-process
worker-2 --> master-process
worker-3 --> master-process
worker-4 --> master-process
worker-5 --> master-process
end

subgraph sqlalchemy
TBD
end
```

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
