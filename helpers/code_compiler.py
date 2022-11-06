"""methods used for communicating with the Judge0 compiler"""

import functools
from typing import List, Union, Tuple
import json
import time

import requests
from helpers import input_generator
from models import website_data

import settings

@functools.lru_cache(maxsize=5)
def get_compiler_status_codes() -> List[dict]:
    pass

@functools.lru_cache(maxsize=5)
def get_active_languages() -> List[dict]:
    endpoint = settings.COMPILER_BASE_URL+'/languages'
    res = requests.get(endpoint)
    if res.status_code == 200:
        # remove the entries that aren't programming languages
        lang_list = [
            i for i in res.json() if i['name'].lower() not in [
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
    elif data.input_type == 2:  # array
        return input_generator.generate_array_inputs(
            arr_info=data.array_details,
            num_inputs=settings.MAX_INPUTS,
        )
    else:
        return None

@functools.lru_cache(maxsize=16384)
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
    # cannot 'await' Requests modules because it's not async
    # --- use an async Requests libaray ---> httpx
    res = requests.post(endpoint, json=request_body).json()
    if 'token' in res:
        return res['token']
    return None

@functools.lru_cache(maxsize=16384)
def get_submission_result(token: str) -> Union[Tuple[float, float], None]:
    # gets the result of a created submission using the token
    endpoint = settings.COMPILER_BASE_URL+'/submissions/'+token
    
    res = requests.get(endpoint)
    if res.status_code == 200:
        res_json = res.json()
        # check the status
        if res_json['status']['id'] in [1, 2]:
            # in queue or processing
            # check if there is a timeout
            # wait for the timeout seconds and call itself?
            time.sleep(2)
            return get_submission_result(token)
        elif res_json['status']['id'] == 3:
            # successfully ran and accepted
            return float(res_json['time']), float(res_json['memory'])
        else:
            return None
    else:
        return None
