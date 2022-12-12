"""methods used for communicating with the Judge0 compiler"""
# standard library imports
from typing import List, Union, Tuple, Set
import time
import asyncio

# external library imports
import requests
import aiohttp

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

async def create_submission(
    code: str, language_id: str, code_input: str,
    session: aiohttp.ClientSession
) -> str:
    # creates a single submission in the compiler
    endpoint = settings.COMPILER_BASE_URL+'/submissions?'\
        f'base64_encoded=false&wait=false'

    request_body = {
        "source_code": code,
        "language_id": language_id,
        "stdin": code_input,
        "encoded": "false"
    }
    async with session.post(endpoint, json=request_body) as resp:
        result = await resp.json()
        if 'token' in result:
            return result['token']
        return None

async def get_submission_tokens_dict(
    code: str, language_id: str, input_list: List[str]
) -> dict:
    submission_tokens_dict = {}
    tasks = []
    async with aiohttp.ClientSession() as session:
        for inp in input_list:
            tasks.append(
                asyncio.ensure_future(
                    create_submission(
                        code=code,
                        language_id=language_id,
                        code_input=inp,
                        session=session,
                    )
                )
            )

        submissions_list = await asyncio.gather(*tasks)
        for i, token in enumerate(submissions_list):
            if token:
                submission_tokens_dict[token] = input_list[i]
    return submission_tokens_dict

async def get_submission_result(
    token: str, session: aiohttp.ClientSession
) -> Tuple[bool, Union[float, None]]:
    # gets the result of a created submission using the token
    endpoint = settings.COMPILER_BASE_URL+'/submissions/'+token
    
    async with session.get(endpoint) as result:
        if result.status == 200:
            res_json = await result.json()
            # check the status
            if res_json['status']['id'] in [1, 2]:
                await asyncio.sleep(1)
                return await get_submission_result(token, session)
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

async def get_runtimes_from_tokens(
    tokens_dict: dict
) -> Union[List[str], Set[str]]:
    runtime_list = []
    error_set = set()
    tasks = []
    code_input = []
    async with aiohttp.ClientSession() as session:
        for token in tokens_dict:
            code_input.append(tokens_dict[token])
            tasks.append(
                asyncio.ensure_future(
                    get_submission_result(token, session)
                )
            )

        submission_results = await asyncio.gather(*tasks)
        for i, (status, output) in enumerate(submission_results):
            if status:
                runtime_list.append([code_input[i], output])
            else:
                error_set.add(output)

    if len(runtime_list) >= len(tokens_dict)//2:
        # ignore errors if at least half of the inputs ran successfully
        return False, runtime_list
    # otherwise return errors
    return True, error_set
