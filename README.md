# Calendar Web App
Calendar Web App to add events either by manual entry or by importing data from CSV file

App Link: https://calendar-web-app-8f07bae2734c.herokuapp.com/

![Screenshot 2024-10-22 at 10 05 43 PM](https://github.com/user-attachments/assets/0910076b-c721-4341-abdb-777fa5724585)


## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Virtualenv Environment](#virtualenv-environment)
- [Project Layout](#project-layout)
- [Details](#details)
- [Deployment](#deployment)
- [Discussion](#discussion)
- [Screenshots](#screenshots)


## Features

- Login/Register using Email or Google OAuth
- Email Reminders to notify users about any upcoming event
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
8. Upload sample csv files present in dummy_events folder for testing bulk upload functionality
9. Keep the app running in order for the email service to work, which will remind users of any upcoming events

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
│   ├── calendar_helper.py # CRUD for calendar resources
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

A. Normal Registration
1. Enter Name, Email, Password and register your details
2. Go to Log In page, and enter Email and Password to Log In
3. Play around with the Calendar by adding events or uploading CSV files
4. Log out to sign out of the app


B. Google OAuth
1. Go to Log In page, click on Login with Google to select google account to log in with
2. Same as normal registration

## Deployment

Successfully deployed on Heroku
App Link: https://calendar-web-app-8f07bae2734c.herokuapp.com/

## Discussion

I have used Flask as my choice of backend for this application because of its vast community and easy setup. I have thoroughly followed the official documentation of Flask to setup a basic flask application and work on top of it to create CRUD operations for calendar events and integrating google Oauth . Initially, I was thinking to integrate a separate front-end project but due to lack of time, I decided to serve templates from Flask application  itself. Thats when FullCalendar.io came to rescue. Its a clean, simple Calendar UI library which allows a lot of customization. Integrating Google Oauth was quite a challenge specially because I had never integrated any authentication service before but overall, it was  a great learning experience. 

I have used SendGrid for the setting up the email service to notify users about the upcoming events, as of now the events which are upcoming in next 2 days, users will be notified about them via email with the help of SendGrid client

In the end, I tried deploying the app to Herokus but after many retries, I was not able to make it run and therefore decided to pass the files but meanwhile, I will keep trying to make Heroku work. Overall, this project was a great learning experience for me irrespective of the outcomes from this assessment.



## Screenshots

Screenshots of different views of the application can be found in folder screenshots
