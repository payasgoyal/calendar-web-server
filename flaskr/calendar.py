import json
import collections
import csv
from io import StringIO
import pandas as pd

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, request, jsonify, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.auth import login_required

from datetime import datetime, timedelta

bp = Blueprint('calendar', __name__, url_prefix='/cal')

@bp.route("/", methods=("GET", "POST"))
@login_required
def show_cal():
    db = get_db()
    current_app.logger.debug(session["user_id"])
    events_rows = db.execute("SELECT * FROM event WHERE user_id = ?", (session["user_id"],)).fetchall()
    events_list = []
    for row in events_rows:
        d = collections.OrderedDict()
        d["id"] = row["id"]
        d["start"] = row["start"]

        end_date = datetime.strptime(row["end"],"%Y-%m-%d")
        end_date_plus_one = end_date + timedelta(days=1)
        d["end"] = end_date_plus_one.strftime("%Y-%m-%d")
        d["title"] = row["title"]
        d["display"] = row["display"]
        d["classNames"] = "id-" + str(row["id"])
        events_list.append(d)
    # current_app.logger.debug(events_list)
    return render_template("calendar/calendar.html", events = events_list)

@bp.route("/create", methods=['POST'])
@login_required
def create_event():
    db = get_db()
    if request.method == "POST": 
        try:
            data = request.get_json()
            current_app.logger.debug(data)

            date_start = data['date_start']
            date_end = data['date_end']
            event_title = data['event_title']
            display = data['display']

        except (KeyError, json.JSONDecodeError) as e:
            current_app.logger.error(f"Error parsing JSON: {str(e)}")
            return jsonify({'error': 'Invalid JSON data!'}), 400

        # store event to database
        db.execute("INSERT INTO event (user_id, start, end, title, display) VALUES (?, ?, ?, ?, ?)", 
                    (session['user_id'], date_start, date_end, event_title, display))
        db.commit()

        # ajax
        if date_start and date_end and event_title:
            return jsonify({'start':date_start, 'end':date_end, 'title':event_title, 'display':display})
        return jsonify({'error' : 'Missing data!'})

# delete event
@bp.route("/delete", methods=['POST'])
def delete_event():
    try:
        data = request.get_json()
        current_app.logger.debug(data)
        id = data["id"]
        # delete event from db
        db = get_db()
        db.execute("DELETE FROM event WHERE id = ? AND user_id = ?", 
            (id, session["user_id"]))
        db.commit()
        return jsonify({ 'success': True, 'message' : 'Event deleted successfully'})
    except Exception as e:
        return jsonify({'success' : False, 'error': str(e)}), 400
        
@bp.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error" : "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        try:
            csv_data = StringIO(file.stream.read().decode("UTF8"), newline=None)
            df=pd.read_csv(csv_data)
            
            required_columns = ['event_title', 'date_start', 'date_end']
            if not all(column in df.columns for column in required_columns):
                return jsonify({
                    "error" : "CSV file is missing required columns"
                }), 400
            
            db = get_db()
            events_added = 0
            for row in df.to_dict('records'):
                db.execute("INSERT INTO event (user_id, start, end, title, display) VALUES (?, ?, ?, ?, ?)", 
                    (session['user_id'], row['date_start'], row['date_end'], row['event_title'], 'block'))
                events_added += 1
            db.commit()
            return jsonify({"message": f"Successfully added {events_added} events"}), 200
        
        except Exception as e:
            current_app.logger.error(f"Error processing CSV: {str(e)}")
            return jsonify(
                {
                    "error" : f"An error occured while processing the CSV: {str(e)}"
                }
            ), 500
        
    return jsonify(
        {
            "error" : "Invalid file format. Please upload a csv file."
        }
    ),400