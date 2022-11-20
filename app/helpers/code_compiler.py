"""methods used for communicating with the Judge0 compiler"""
# standard library imports
from typing import List, Union, Tuple, Set
import time

# external library imports
import requests

# internal imports
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

def create_submission(code: str, language_id: str, code_input: str) -> str:
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

def get_submission_tokens_dict(
    code: str, language_id: str, input_list: List[str]
) -> dict:
    submission_tokens_dict = {}
    for inp in input_list:
        if (token:=create_submission(
            code=code,
            language_id=language_id,
            code_input=inp,
        )):
            submission_tokens_dict[token] = inp
    return submission_tokens_dict

def get_submission_result(token: str) -> Tuple[bool, Union[float, None]]:
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
            return (True, float(res_json['time']))
        elif res_json['status']['id'] == 5:
            # time limit exceeded
            return (False, res_json['message'])
        else:
            # runtime error occured
            return (False, res_json['stderr'])
    else:
        # error occurred in the request
        raise Exception(
            f'error occurred while fetching submission result:\n{result.text}'
        )

def get_runtimes_from_tokens(tokens_dict: dict) -> Union[List[str], Set[str]]:
    runtime_list = []
    error_set = set()
    for token in tokens_dict:
        code_input = tokens_dict[token]
        status, output = get_submission_result(token)
        if status:
            runtime_list.append([code_input, output])
        else:
            error_set.add(output)
    if len(runtime_list) >= len(tokens_dict)//2:
        # ignore errors if at least half of the inputs ran successfully
        return False, runtime_list
    # otherwise return errors
    return True, error_set
