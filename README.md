# Calendar Web App
Calendar Web App to add events either by manual entry or by importing data from CSV file

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Virtualenv Environment](#virtualenv-environment)
- [Project Layout](#project-layout)
- [Details](#details)
- [Discussion](#discussion)


## Features

- Login/Register using Email or Google OAuth
- Email Reminders to notify about any upcoming event
- Manual Entry for multi-day event or single day event
- Bulk upload of events using CSV file

## Setup

The project has been developed on MacOS with Apple Silicon(M1), but should work without problems on Windows too.

0. You need to have Python (3.10 or greater) installed
1. Clone or download the repository to wherever you want to install it
2. Create a virtual environment. Refer the ***Virtualenv Environment*** section below
3. Run `pip install -r requirements.txt` to install the required dependencies
4. Ensure there is .env file present in root directory of the project as it contains all the secrets needed for Google OAuth and SendGrid Email Service
5. In terminal, run command "flask --app flaskr init-db" to Initialize the database file in instance folder
6. Run "flask --app flaskr run" to launch the application
7. Launch your browser and enter 'http://127.0.0.1:5000/' in url

## Virtualenv Environment

1. Create the virtual environment:
```bash
$ python3 -m venv venv
```

2. Activate it:
```bash
$ source venv/bin/activate
```

3. Install dependencies (in the virtual environment):
```bash
(.venv) $ pip install -r requirements.txt
```
4. To Deactivate virtual environment
```bash
$ deactivate
```

## Project Layout
```
/flask-calendar
├── flaskr/
│   ├── __init__.py # initialize flask app
│   ├── db.py # database related configuration
│   ├── schema.sql # database schematics 
│   ├── auth.py # registration and login related 
│   ├── calendar.py # CRUD for calendar resources
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   └── calendar/
│   │       └── calendar.html # js code and calendar view here 
│   └── static/
│       └── style.css    
├── instance/ 
│   ├── flaskr.sqlite # sqlite db for storing events
├── venv/ # virtual environment
├── .gitignore  # define what files we don't need to commit
├── package-lock.json # js package manager
├── README.md
└── Procfile  # for Heroku Deployment
```

## Details

1. Normal Registration
a. Enter Name, Email, Password and register your details
b. Go to Log In page, and enter Email and Password to Log In
c. Play around with the Calendar by adding events or uploading CSV files
d. Log out to sign out of the app


2. Google OAuth
a. Go to Log In page, click on Login with Google to select google account to log in with
b. Same as normal registration

## Discussion

I have used Flask as my choice of backend for this application because of its vast community and easy setup. I have thoroughly followed the official documentation of Flask to setup a basic flask application and work on top of it to create CRUD operations for calendar events and integrating google Oauth . Initially, I was thinking to integrate a separate front-end project but due to lack of time, I decided to serve templates from Flask application  itself. Thats when FullCalendar.io came to rescue. Its a clean, simple Calendar UI library which allows a lot of customization. Integrating Google Oauth was quite a challenge specially because I had never integrated any authentication service before but overall, it was  a great learning experience. 

In the end, I tried deploying the app to Heroku but after many retries, I was not able to make it run and therefore decided to pass the files but meanwhile, I will keep trying to make Heroku work. Overall, this project was a great learning experience for me irrespective of the outcomes from this assessment. I would like to thank Animoca Brands to give me a chance.