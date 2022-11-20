"""this file contains models to wrap data in the structure expected
by the website"""

# standard library imports
from typing import Optional, Union

# external library imports
from pydantic import BaseModel


class CodeSubmissionStringDetails(BaseModel):
    characters_allowed: str
    max_length: int


class CodeSubmissionNumberDetails(BaseModel):
    numbers_allowed: str
    range_start: Union[int, float]
    range_end: Union[int, float]


class CodeSubmissions(BaseModel):
    """format of the request sent by the website with code and test
    case description"""
    code: str
    input_type: int
    language_id: int
    string_details: Optional[CodeSubmissionStringDetails]
    number_details: Optional[CodeSubmissionNumberDetails]
