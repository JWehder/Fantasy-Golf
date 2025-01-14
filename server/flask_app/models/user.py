from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional, Union
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import bcrypt
import os
import sys
from email_validator import validate_email, EmailNotValidError
import random
import string

# Adjust the paths for MacOS to get the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.base_model import Base
from models import PyObjectId 
from config import db
from helper_methods import send_email

class User(Base):
    id: Optional[PyObjectId] = Field(alias='_id')
    Username: str
    Email: EmailStr
    Password: str
    Teams: List[Union[PyObjectId, str, dict]] = []
    VerificationCode: Optional[str] = 0
    IsVerified: bool
    VerificationExpiresAt: Optional[datetime]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    def to_dict(self):
        # Filter the dictionary to return only the necessary fields
        user_dict = super().to_dict()
        # Extract only the fields you want (id, Username, and Email)
        return {
            "id": str(self.id),
            "Username": self.Username,
            "Email": self.Email
        }

    def save(self):
        """Insert or update a user"""
        self.updated_at = datetime.utcnow()
        if not self.created_at:
            self.created_at = self.updated_at

        user_data = self.dict(by_alias=True, exclude_unset=True)
        if '_id' in user_data and user_data['_id']:
            # Update existing user
            result = db.users.update_one({'_id': user_data['_id']}, {'$set': user_data})
            if result.matched_count == 0:
                raise ValueError(f"User not found with _id: {user_data['_id']}")
        else:
            # Insert new user
            result = db.users.insert_one(user_data)
            self.id = result.inserted_id
        return self.id

    def send_verification_email(self):
        email = self.Email

        # Check if the temporary user id exists in the database
        user = db.users.find_one({"Email": email})
        if not user:
            print(f"User with email {email} not found.")
            return {"error": "Email not found."}
        else:
            print(f"User found: {user}")

        # Generate a new verification code
        new_verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Update the user's verification code (case-insensitive match for email)
        db.users.update_one(
            {"Email": email},  # assuming case-sensitivity is not the issue
            {"$set": {
                "VerificationCode": new_verification_code
            }}
        )

        subject = "Email Verification Code"
        body = f"""
        <p>Hello {self.Username},</p>
        <p>Your new email verification code is <b>{new_verification_code}</b>.</p>
        <p>Please enter this code to verify your email address.</p>
        <p>If you didn't sign up for this account, you can safely ignore this email.</p>
        <p>Thank you!</p>
        """

        # Use your email sending function here
        send_email(subject, email, body)

        # Once the email has been sent, give the user 60 seconds to 
        # send back the verification code.
        db.users.update_one(
            {"Email": email},  # assuming case-sensitivity is not the issue
            {"$set": {
                "VerificationExpiresAt": datetime.utcnow() + timedelta(seconds=60)
            }}
        )

    def hash_password(self, password: str) -> str:
        """Hash a plain text password"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        print(password, self.Password)
        """Check a plain text password against the stored hashed password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.Password.encode('utf-8'))

    @field_validator('Username')
    def validate_username_length(cls, v):
        """Ensure username is at least 5 characters long"""
        if len(v) < 5 or len(v) > 50:
            raise ValueError('Username length must be between 5 and 50 characters.')
        return v

    @field_validator('Email')
    def validate_email_and_deliverability(cls, v):
        """Ensure that the email is valid and deliverable"""
        try:
            # Check that the email address is valid. Turn on check_deliverability
            emailinfo = validate_email(v, check_deliverability=True)

            # After this point, use only the normalized form of the email address,
            # especially before going to a database query.
            email = emailinfo.normalized
            return email

        except EmailNotValidError as e:

            # The exception message is human-readable explanation of why it's
            # not a valid (or deliverable) email address.
            return str(e)

    @field_validator('Password')
    def validate_password_strength(cls, v):
        """Ensure password meets complexity requirements"""
        if len(v) < 8 or len(v) > 65:
            raise ValueError('Password must be between 8 and 50 characters.')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter.')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit.')
        if not any(char in "!@#$%^&*()-_+=" for char in v):
            raise ValueError('Password must contain at least one special character.')
        return v