"""this file contains all the pydantic models used for judge0"""
# standard libarary imports
from typing import List
# external imports
from pydantic import BaseModel
# internal imports
from helpers import custom_exceptions

class ActiveLanguagesListItem(BaseModel):
    id: str
    name: str


# might not need the ActiveLanguageList model (and the parse fn)
# might just return the json that is returned by judge0
class ActiveLanguagesList(BaseModel):
    """response structure of judge0 languages endpoint"""
    __root__: List[ActiveLanguagesListItem]


def parse_to_active_language_model(data: List[dict]) -> ActiveLanguagesList:
    try:
        return ActiveLanguagesList.parse_obj(data).__root__
    except Exception as e:
        raise custom_exceptions.ParsingToPydanticModelException(data, e)
