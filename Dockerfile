FROM python:3.9.5

EXPOSE 5000

WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# command: flask db migrate
CMD [ "flask", "db" , "migrate" ]