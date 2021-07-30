# THE TIME GAME API

This repository contains the code for the awesome  [The Time Game](https://time-game.herokuapp.com/) that we are still building.

Basically, it's a simple API over Flask written in Python that allows users to log in, pick themes to play, fetch and answer the questions, etc.

## Install dependencies
The project is written in Python and uses the [Flask](http://flask.pocoo.org/) microframework.
  ### Set up virtual environment
  ```
  python3 -m venv venv
  python venv/bin/activate
  pip install -r requirements.txt
  ```
  This way you will have a virtual environment with all the dependencies installed.

## Env variables
To run the server make sure you have [PostgreSQL](https://www.postgresql.org/) installed and running. Then create a new database called `the_time_game`.

You need to set the following environment variables inside a file called `.env` in the project root:
```
FLASK_APP=app
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=postgresql://{database_user_name}:{db_user_name}@localhost/the_time_game
SECRET_KEY=top secret
DATABASE_URI=localhost
DATABASE_PASSWORD={database_password}
DATABASE_PORT=5432
DATABASE_NAME=the_time_game
DATABASE_USER={database_user_name}
```

## Run the server


```
flask run
```

## Production

There's a `docker-compose.prod.yml` file that will run the server in production mode, which also consumes `.env.prod`. This file is not in the repository.

# SSL Certificate

In order to use the api in real wolrd you need to generate a SSL certificate. The easiest way to do this is using the [Let's Encrypt](https://letsencrypt.org/) service that is provided by [Certbot](https://certbot.eff.org/).

To do this, you need to have a domain name that points to the server and get into the ngnix container like this:

```
docker exec -it <nginx_container_name> bash
```

Once inside the container, you need to install the certbot package:

```
apt-get update
apt-get install python-certbot-nginx certbot
```

Then run the following command:

```
certbot --nginx
```

And follow the instructions.