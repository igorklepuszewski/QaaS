# QaaS
# Prerequisites

- Python 3.11
- Poetry
# How to run?

Confidential keys have to be loaded as environment variables. Supplied view .env file

## Development

### Database

```
$ docker-compose up -d db
```

### Backend

```
$ cd backend
$ pipenv install --dev
$ pipenv shell
$ python manage.py runserver
```


## Manage db

```
$ docker exec -it <container_id> psql -U <database> -W <user>
```

# API STRUCTURE

```
/api/quizzes
```
GET
Allowed for creator, participants

See relevant quizzes

POST
Allowed for a creator

EXAMPLE BODY:
```
{
    "name": "test",
    "invitees": [
        {
            "email": "test@gmail.com"
        }
    ],
    "questions": [
        {
            "text": "IS IT ANY GOOD?",
            "answers": [
                {
                    "text": "YES",
                    "is_correct": true
                },
                {
                    "text": "NO",
                    "is_correct": false
                }
            ]
        },
        {
            "text": "IS IT ANY BAD?",
            "answers": [
                {
                    "text": "YES",
                    "is_correct": false
                },
                {
                    "text": "NO",
                    "is_correct": true
                }
            ]
        }
    ]
}
```


