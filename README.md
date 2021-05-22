This repository intends to implement the API for Collective Intelligence Metre Services.

To run this repository it is recommended to follow these steps unless you know better ones:

1. Install docker and docker compose
2. Create a python virtual environment
3. Activate your virtual environment
4. Execute sudo docker-compose up -d
5. If it is the first time you will need to create the volumes the console will tell you to create and run docker-compose up again until you get no errors
6. If it is the first time you will also need to execute
$ sudo docker exec -it django_container_name /bin/bash
$ cd app
$ python3 manage.py migrate

This applies the migrations to the database

