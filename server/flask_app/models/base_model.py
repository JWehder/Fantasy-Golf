from bson import ObjectId
from pydantic import BaseModel
import os
import sys

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helper_methods import to_serializable, serializable_for_db

class Base(BaseModel):

    def to_dict(self):
        return to_serializable(self.__dict__)

    def to_dict_for_mongodb(self):
        return serializable_for_db(self.__dict__)