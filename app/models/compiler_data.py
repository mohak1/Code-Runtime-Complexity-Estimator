"""this file contains all the pydantic models used for judge0"""
# standard libarary imports
from typing import List

# external imports
from pydantic import BaseModel

class ActiveLanguagesListItem(BaseModel):
    id: str
    name: str

class ActiveLanguagesList(BaseModel):
    """response structure of judge0 languages endpoint"""
    __root__: List[ActiveLanguagesListItem]
