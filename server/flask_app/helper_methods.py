from flask_mailman import EmailMessage
from bson import ObjectId
import pytz
from datetime import datetime, timedelta

# Add this line to ensure the correct path
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import db

def send_email(subject: str, recipient: str, body_html: str):
    """Send an email."""
    msg = EmailMessage(
        subject=subject,
        to=[recipient],
        body=body_html,
    )

    # Set the content type to 'html' so that the email is rendered as HTML
    msg.content_subtype = 'html'

    try:
        msg.send()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_all_tournament_ids():
    tournaments_collection = db.tournaments
    tournament_ids = tournaments_collection.distinct('_id')
    return [ObjectId(tid) for tid in tournament_ids]

def get_day_number(day_name: str) -> int:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days.index(day_name)

def convert_utc_to_local(utc_dt, user_tz):
    local_tz = pytz.timezone(user_tz)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_dt

def to_serializable(data):
    from models import Base

    # Check if data is a dictionary and traverse
    if isinstance(data, dict):
        return {key: to_serializable(value) for key, value in data.items()}
    elif isinstance(data, Base): 
        return to_serializable(data.__dict__)
    # Check if data is a list and traverse
    elif isinstance(data, list):
        return [to_serializable(item) for item in data]
    # Convert ObjectId to string
    elif isinstance(data, ObjectId):
        return str(data)
    # Convert datetime to ISO format
    elif isinstance(data, datetime):
        return data.strftime("%m/%d/%Y")
    # Return data if no conversion is needed
    else:
        return data

def convert_to_datetime(self, day_of_week: str, time_str: str, timezone_str: str) -> datetime:
        day_number = get_day_number(day_of_week)
        time_parts = time_str.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        
        now = datetime.now(pytz.timezone(timezone_str))
        current_day_number = now.weekday()
        
        days_ahead = day_number - current_day_number
        if days_ahead <= 0:
            days_ahead += 7

        draft_start = now + timedelta(days=days_ahead)
        draft_start = draft_start.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return draft_start