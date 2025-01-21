from bson import ObjectId
from pydantic import BaseModel, PrivateAttr
import os
import sys

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helper_methods import to_serializable

class Base(BaseModel):
    _instances: dict = PrivateAttr(default={})  # A dictionary to store instances by class

    def to_dict(self):
        return to_serializable(self.__dict__)