# GraphQL API for gluons

This application is on Django with graphene-django

## Project name on Django

gluons

## Application name on Django

graphql_api

## Requirements

* python3
* pip
* Postgresql
* Pgroonga (全文検索エンジン）

## Rely on Postgresql Database

* database: gluons
* user:     gluons
* host:     localhost
* port:     5432
* engine:   django.db.backends.postgresql_psycopg2

### How to start postgresql

```
$ brew services start postgresql
```


## Preparation

```
$ git clone git@github.com:euonymus-prod/gluons_graphql.git
$ cd gluons_graphql
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Run server

```
$ source venv/bin/activate
$ cd [path to repo]/gluons
$ python manage.py runserver
```

## How to Access

Use Insomnia.
You can make GraphQL call to
http://localhost:8000/graphql/
