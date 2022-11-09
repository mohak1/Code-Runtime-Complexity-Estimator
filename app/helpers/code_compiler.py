"""methods used for communicating with the Judge0 compiler"""
from typing import List, Union, Tuple
import time

import requests

from app.helpers import input_generator
from app.models import website_data
import app.settings as settings

def get_active_languages() -> List[dict]:
    endpoint = settings.COMPILER_BASE_URL+'/languages'
    result = requests.get(endpoint)
    if result.status_code == 200:
        # remove the entries that aren't programming languages
        lang_list = [
            i for i in result.json() if i['name'].lower() not in [
                'executable', 'plain text']
        ]
        return lang_list
    else:
        return None

def generate_inputs_for_code(
    data: website_data.CodeSubmissions,
) -> Union[List, None]:
    # returns all generated input cases
    if data.input_type == 0:    # string
        return input_generator.generate_string_inputs(
            str_info=data.string_details,
            num_inputs=settings.MAX_INPUTS,
        )
    elif data.input_type == 1:  # number
        return input_generator.generate_number_inputs(
            num_info=data.number_details,
            num_inputs=settings.MAX_INPUTS,
        )
    else:
        return None

def create_submission( code: str, language_id: str, code_input: str) -> str:
    # creates a single submission in the compiler
    endpoint = settings.COMPILER_BASE_URL+'/submissions/?'\
        f'base64_encoded=false&wait=false'

    request_body = {
        "source_code": code,
        "language_id": language_id,
        "stdin": code_input,
        "encoded": "false"
    }
    result = requests.post(endpoint, json=request_body).json()
    if 'token' in result:
        return result['token']
    return None

def get_submission_result(token: str) -> Union[float, None]:
    # gets the result of a created submission using the token
    endpoint = settings.COMPILER_BASE_URL+'/submissions/'+token
    
    result = requests.get(endpoint)
    if result.status_code == 200:
        res_json = result.json()
        # check the status
        if res_json['status']['id'] in [1, 2]:
            # wait for two seconds and check again
            time.sleep(2)
            return get_submission_result(token)
        elif res_json['status']['id'] == 3:
            # successfully ran and accepted
            return float(res_json['time'])
        else:
            return None
    else:
        return None
