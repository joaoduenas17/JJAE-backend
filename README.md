### Running project

**First time only:**  
You need to create an **env** folder, copy file **env.example** (from **code_project** directory) inside it with name dev.env or staging.env, and update values accordingly (for example, put DJANGO_SETTINGS_MODULE=init_project.settings for development).

# Start with venv

You must install python 3.8

Step for first time

- python -m venv .venv
- source .venv/bin/activate
- pip install -r back_project/requirements/dev.txt
- cd back_project/app
- python manage.py createsuperuser
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

Step for up
- python -m venv .venv
- source .venv/bin/activate
- cd back_project/app
- python manage.py runserver

# Start with docker compose

First

- docker-compose -f dev.yml up --build

You should enter the container for execute commands

- docker-compose -f dev.yml exec h_tierra_back /bin/bash
or
- docker-compose -f dev.yml exec h_tierra_back //bin//bash

then, execute commands  
- python manage.py collectstatic --no-input
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver 0.0.0.0:8000
create super user
- python manage.py createsuperuser

If you have create the container only you need execute this:

For stop containers (and not require image creation again):  
- docker-compose -f dev.yml stop`

For start containers (using existing image):  
- docker-compose -f dev.yml start`


When requirements file change (then, create the image again):
- docker-compose -f dev.yml up --build

### Notes:

To see database information, access to http://localhost:8080 with:
POSTGRES_DB=cohe
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
DB_HOST=todoklikers_db

To access to API documentation in `swagger/`, make login via `admin/` first (access is restricted to authenticated users)
