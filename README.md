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
$ poetry install
$ poetry shell
$ python manage.py migrate
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
Possible query params
```
creator [email], participant[email], name [str]
```

POST

Allowed for a creator

Create a new quizz

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


```
/api/quizzes/<int:pk>/
```

GET

Allowed for creator and participants

See individual quiz


```
/api/votes/
```

GET

Possible query params
```
participant [email], question [id], quiz [id], answer[id]
```


Get the votes for quizzes that you have created if you are creator
Get the votes you have submitted if you are a participant

```
/api/quiz-progress/
```
GET

Allowed for a creator and participant

Needs a body
Example:
```
{
    "quiz_id": 47
}
```

Get your quiz progress if you are participant or the overall quiz progress if you are a creator

```
/api/quiz-scores/
```
GET
Allowed for a creator and participant

Needs a body
Example:
```
{
    "quiz_id": 47
}
```

Get your quiz score if you are participant or the overall quiz score if you are a creator


```
/api/usage/
```
GET

Allowed for an admin

Needs a body
Example:
```
{"date":"2023-07-12", "format": "csv"}
```

Format can be eihter csv or json

Send a request for a usage, get the response with the url to the file

```
/api/users/
```
GET

Possible query params
```
participants [Any], username [str], email [str]
```

Allowed for an creator


Get the users that have been invited to the quiz, can be filter down to the users that have participated.
Or target specific user by username or email.



```
/api/send-quiz-result/<int:quiz_id>/
```
POST

Allowed for a creator

Request email sendout of the results to all the participant of the quiz.


```
/api/quiz-submission/
```
POST

Allowed for the participant

Needs a body
Example:
```
{
    "quiz_id": 47,
    "answers_id": [
        74,75
    ]
}
```

Send the answers for the quiz in order to take part in quiz


```
/api/whoami/
```
GET

Allowed for admin

Needs a body
Example:
```
{"email":"test@test.com"}
```

Get the authentication token for a user


# HOW TO OPERATE

- create superuser
- find out the auth Token for the superuser

```
from user.models import User
from rest_framework.authtoken.models import Token
user = User.objects.get(email=super_user_email)
token, _ = Token.objects.get_or_create(user=user)
print(token)
```
- in request headers pass additional key value pair "Authorization": "Token [super_user_token]"
- after that you can find out other users Tokens via `/api/whoami/`
- create a quiz, invite other users...