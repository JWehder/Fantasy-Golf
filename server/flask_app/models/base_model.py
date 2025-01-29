from bson import ObjectId
from pydantic import BaseModel, PrivateAttr
import os
import sys

# Adjust the paths for MacOS to get the flask_app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helper_methods import to_serializable

class Base(BaseModel):

    def to_dict(self):
        return to_serializable(self.__dict__)

    class Config:
        arbitrary_types_allowed = True  # Allow non-Pydantic types (e.g., ObjectId)
        allow_population_by_field_name = True  # Allow field names to be populated by alias
        extra = "allow"  # Ignore unexpected fields instead of raising validation errors