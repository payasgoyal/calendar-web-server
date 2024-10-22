import os
import pathlib
from flask import Flask
from flask_cors import CORS
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flaskr.calendar_helper import *
from flaskr.auth import *
from dotenv.main import load_dotenv


load_dotenv(dotenv_path='../.env')
SENDGRID_KEY = os.getenv('SENDGRID_KEY')

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    scheduler = BackgroundScheduler()
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # check whether the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        return redirect("/cal")
    
    from . import db
    db.init_app(app)

    #register blueprint "auth"
    from . import auth
    app.register_blueprint(auth.bp)

    #register blueprint "calendar_helper"
    from . import calendar_helper
    app.register_blueprint(calendar_helper.bp)

    with app.app_context():

        def send_email(to_email, subject, body):
            smtp_server = "smtp.sendgrid.net"
            smtp_port = 587
            smtp_username = "apikey"
            from_email = "goyal.payas2000@gmail.com"

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            try:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_username, SENDGRID_KEY)
                    server.send_message(msg)
                print(f"Email sent successfully to {to_email}")
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

        def mark_event_as_notified(event_id):
            db = get_db()
            try:
                db.execute("UPDATE event SET notified = 1 WHERE id = ?", (event_id,))
                db.commit()
                print(f"Event {event_id} marked as notified successfully.")
                return True
            except Exception as e:
                db.rollback()
                print(f"Error marking event {event_id} as notified: {str(e)}")
                return False
        
        def get_upcoming_events(time_threshold=timedelta(days=2)):
            now = datetime.now().date()
            future = now + time_threshold

            db = get_db()
            try:
                query = """
                SELECT * FROM event 
                WHERE date(start) BETWEEN date(?) AND date(?) 
                AND notified = 0
                """
                events_rows = db.execute(query, (now.isoformat(), future.isoformat())).fetchall()
                return [dict(row) for row in events_rows]
            except Exception as e:
                print(f"Error fetching upcoming events: {str(e)}")
                return None
        
        def get_user_by_id(user_id):
            db = get_db()
            try:
                user_data = db.execute(
                    "SELECT id, username, email FROM user WHERE id = ?", 
                    (user_id,)
                ).fetchone()
                
                if user_data:
                    return dict(user_data)
                else:
                    return None
            except Exception as e:
                print(f"Error fetching user with id {user_id}: {str(e)}")
                return None
            
        def check_upcoming_events():
            for _ in (True, ):
                with app.app_context():
                    print("check for upcoming events...", datetime.now())
                    upcoming_events = get_upcoming_events(time_threshold=timedelta(days=2))
                    if upcoming_events is None:
                        print("No upcoming events found or an error occurred while fetching events.")
                        break
            
                    if len(upcoming_events) == 0:
                        print("No events scheduled in the next 2 days.")
                        break
                    
                    for event in upcoming_events:
                        user = get_user_by_id(event['user_id'])
                        if user and user["email"]:
                            subject = f"Upcoming Event: {event['title']}"
                            body = f"Your event '{event['title']}' is starting soon at {event['start']}."

                            send_email(user["email"], subject, body)
                            mark_event_as_notified(int(event['id']))
                            print(f"Notification sent for event: {event['title']}")
        
        scheduler.add_job(check_upcoming_events, 'interval', minutes=60)
        scheduler.start()

    return app