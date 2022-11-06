"""this file contains models to wrap data in the structure expected
by the website"""

from pydantic import BaseModel
from typing import Optional, Union


class LanguagesResponse(BaseModel):
    """format of the active languages list expected by the website"""
    id: str
    name: str


class CodeSubmissionStringDetails(BaseModel):
    characters_allowed: str
    max_length: int


class CodeSubmissionNumberDetails(BaseModel):
    numbers_allowed: str
    range_start: Union[int, float]
    range_end: Union[int, float]


class CodeSubmissionArrayDetails(BaseModel):
    element_type: int
    range_start: Optional[Union[int, float]]
    range_end: Optional[Union[int, float]]
    characters_allowed: Optional[str]
    max_length: Optional[int]


class CodeSubmissions(BaseModel):
    """format of the request sent by the website with code and test
    case description"""
    code: str
    input_type: int
    language_id: int
    string_details: Optional[CodeSubmissionStringDetails]
    number_details: Optional[CodeSubmissionNumberDetails]
    array_details: Optional[CodeSubmissionArrayDetails]


class RunResults(BaseModel):
    """format of the response expected by the website for complexity
    response"""
    ...