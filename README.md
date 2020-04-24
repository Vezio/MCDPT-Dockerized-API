# MCDPT-Dockerized-API
Dockerized service: flask server. The flask server 
is an interface to the MCDPT-Dockerized-DB and future services to come.

Authors: 
Tyler Rimaldi, 
Daniel Grossmann,
Dr. Donald Schwartz

## How to setup this repository
Create an instance folder in `./app/`: `./app/instance`
Inside of the instance folder add the following:
`__init__.py`

`config.py`

Inside the `config.py`, add the following:
```
DEBUG = boolean
SECRET_KEY = "secret"
DB_INTERFACE_URL = "DBURL" #This is your db url, could be localhost or the docker-compose service address.
```

## How to use this repository after setup
In the root directory of this repository, enter the following commands:

`docker-compose build` will build the services

`docker-compose up` will run the services

`localhost:4000` will be the the address to make calls to the connected interfaces (ofcourse
these calls will be those that are defined by the flask server models.)

Do note that you may need to kill and remove the docker images from your machine should you ever go back and make any changes to this repository's contents.

## API Routes Explained

### GET
- `localhost:4000/sessions/<cwid>`: cwid=integer
- `localhost:4000/sessions/shared/<cwid>`: cwid=integer
- `localhost:4000/sessions/get/<cwid>/<sessionNumber>`: {cwid,sessionNumber}=integer

### POST
- `localhost:4000/login/<cwid>/<password>`: cwid=integer, password=alphanumeric
- `localhost:4000/logout`
- `localhost:4000/users/create/<cwid>/<name>/<password>`: cwid=integer, name=alphabetical, password=alphanumeric
- `localhost:4000/sessions/create`
- `localhost:4000/sessions/share/<sessionCWID>/<sessionNumber>/<shareToCWID>`: {cwid,sessionNumber,shareToCWID}=integers, respectively
