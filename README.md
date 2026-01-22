# LesJeunot-Accounts

A Microservice School Project.

# Prerequisites

- [Python](https://www.python.org/downloads) >= 3.11

# Installation

### 1. Install Python for your Operating System

Follow the instructions on the Python website or online.

### 2. Clone the repo

```bash
# HTTPS
git clone https://github.com/SH4DOW4RE/LesJeunot-Accounts.git
# SSH
git clone git@github.com:SH4DOW4RE/LesJeunot-Accounts.git
```

### 3. Create a Virtual Environment and activate it

```bash
python3 -m venv .venv
```

```bash
# Windows
.venv\Scripts\activate.bat
# Linux
.venv/Scripts/activate
```

### 4. Install dependancies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

```
# Host IP and Port to listen on
HOST=0.0.0.0
PORT=8080

# Flask secrets (defaults are randomly generated at boot if omitted)
# SECRET_KEY=<random hex string>
# JWT_SECRET_KEY=<random hex string>
# JWT_ISSUER=lesjeunot.accounts

# Comma-separated list of allowed origins (default: "*")
CORS_ORIGINS=http://localhost:8080

# Encryption key for the users' data (Required)
KEY=<32 bytes encoded in base64>

# MySQL settings
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=lesjeunot
DB_USER=lesjeunot
DB_PASSWORD=<strong password>
```

### 6. Start the service in development mode

> [!NOTE]
> A running MySQL instance matching the environment variables above is required.

```bash
python3 main.py
```

*Production mode coming soon™*

### 7. Profit ?

# Routes

Example baseURL: `http://localhost:8080`

> [!NOTE]
> A newly created JWT access token (`/login`) is considered fresh.<br>
> A JWT refresh token (`/refresh`) is no longer considered fresh.

> [!NOTE]
> Required field: `<data>`<br>
> Optional field: `[data]`

> [!NOTE]
> Keep in mind that any errors not shown as an example are unexpected errors.<br>
> Usually shown as a 500 error.

### Index

`GET /` Ping the server to see if it's online.
<br>
Example 200 response:
```json
{
    "status": 200
}    
```
---
`GET /versions` Lists available versions.
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "versions": [
            "v1"
        ]
    }
}    
```
---
### Users

`POST /<version>/user` Creates a user (register a user).
<br>
Body:
```json
{
    "lastname": "<lastname>",
    "firstname": "<firstname>",
    "age": "<age>",
    "email": "<email>",
    "password": "<password>"
}
```
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "User successfully created."
    }
}
```
Example 400 response:
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "Missing value(s): [<list of missing values>]"
}
```
---
`GET /<version>/user` Get all users (admin only).
<br>
**Authorization header required** `Authorization: Bearer <access token>`
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "users": [
            {
                "uuid": "<uuid>",
                "lastname": "<lastname>",
                "firstname": "<firstname>",
                "age": "<age>",
                "email": "<email>",
                "role": "<role>"
            }
        ]
    }
}
```
Example 403 response:
```json
{
    "status": 403,
    "error": "Forbidden",
    "message": "Admin role required."
}
```
---
`POST /<version>/user/login` Log in a User.
<br>
Body:
```json
{
    "email": "<email>",
    "password": "<password>",
}
```
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "User successfully logged in.",
        "token": {
            "access": "<JWT access token (valid for 6 hours)>",
            "refresh": "<JWT refresh token (valid for 7 days)>",
        }
    }
}    
```
Example 400 response:
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "Missing value(s): [<list of missing values>]"
}
```
Example 401 response:
```json
{
    "status": 401,
    "error": "Unauthorized",
    "message": "Email or Password invalid."
}
```
---
`GET /<version>/user/refresh` Gives a new Access Token from a Refresh Token.
<br>
**Authorization header required** `Authorization: Bearer <refresh token>`
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "token": {
            "access": "<JWT access token (valid for 6 hours)>"
        }
    }
}    
```
---
`GET /<version>/user/me` Get the logged in User's details.
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "lastname": "<lastname>",
        "firstname": "<firstname>",
        "age": "<age>",
        "email": "<email>",
        "role": ""
    }
}    
```
---
`PUT /<version>/user/modify` Modify all of the User's details.
<br>
Body:
```json
{
    "lastname": "<lastname>",
    "firstname": "<firstname>",
    "age": "<age>",
    "email": "<email>",
    "password": "<password>"
}
```
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "User successfully modified."
    }
}
```
Example 400 response:
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "Use PATCH for partial modification of user data."
}
```
---
`PATCH /<version>/user/modify` Modify some values of the User's details.
<br>
*All fields are optional, but at least one is required.*
<br>
Body:
```json
{
    "lastname": "[lastname]",
    "firstname": "[firstname]",
    "age": "[age]",
    "email": "[email]",
    "password": "[password]"
}
```
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "User successfully modified."
    }
}
```
Example 400 response:
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "At least one field is required."
}
```
---
`GET /<version>/user/delete` Delete the current User (logged in user).
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "User successfully deleted."
    }
}
```
---
### Tickets

`GET /<version>/ticket` Get all the User's tickets.
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "showings": [<list of string of the showing values>]
    }
}
```
---
`GET /<version>/ticket?scope=all` Get every ticket (admin only).
<br>
**Authorization header required** `Authorization: Bearer <access token>`
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "tickets": [
            {
                "uuid": "<ticket uuid>",
                "user_id": "<owner uuid>",
                "showing": "<showing value or JSON>"
            }
        ]
    }
}
```
Example 403 response:
```json
{
    "status": 403,
    "error": "Forbidden",
    "message": "Admin role required."
}
```
---
`GET /<version>/ticket/<ticket uuid>` Get a User's specific ticket.
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "showings": "<showing value>"
    }
}
```
---
`POST /<version>/ticket` Creates a ticket.
<br>
Body:
```json
{
    "showing": "<showing value>"
}
```
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "Ticket successfully created.",
        "uuid": "<ticket's uuid>"
    }
}
```
Example 400 response:
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "Missing value: showing"
}
```
---
`GET /<version>/ticket/delete/[id]` Delete a specified ticket, or all tickets if not speficied.
<br>
Example 200 response:
```json
{
    "status": 200,
    "data": {
        "message": "Ticket successfully deleted."
    }
}
```
