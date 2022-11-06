"""this is the entrypoint file"""
# standard library imports
import json

# external library imports
from typing import Any
from fastapi import FastAPI, Response, status
import requests

# internal imports
from models import compiler_data, website_data
from helpers import input_generator as ig
from helpers import code_compiler
from helpers import model_fitting

app = FastAPI(debug=True)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def base_url():
    # include a list of the available endpoints
    return 'available endpoints are: "/healthy", "ect"'

@app.get('/healthy')
def health_check():
    return True


@app.get('/get_active_languages', status_code=status.HTTP_200_OK)
def programming_languages(response: Response):
    # return the data by judge0
    # or an error code if fetch if not successful
    if language_list:=code_compiler.get_active_languages():
        return language_list
    # noitify that the compiler is down

    # -----SEND A DISCORD/SLACK NOTIFICATION-----

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return None


@app.post('/estimate_complexity', status_code=200)
# decorator for catch-all exceptions
async def estimate_complexity(
        data: website_data.CodeSubmissions,
        response: Response
    ):
    # gether inputs for the code
    if not (input_list := code_compiler.generate_inputs_for_code(data)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "`input_type` value not recognised"
    
    # submit inputs to the compiler
    breakpoint()
    submission_tokens_dict = {}
    for inp in input_list:
        if (token:=code_compiler.create_submission(
            code=data.code,
            language_id=data.language_id,
            code_input=inp,
        )):
            submission_tokens_dict[token] = inp

    is_input_case_string = False
    if data.input_type == '0': # string; compare against length
        is_input_case_string = True
    elif data.input_type == '1': # number: compare against number
        is_input_case_string = False
    elif data.input_type == '2':
        if data.array_details.element_type in [1, 2]: # number;
            is_input_case_string = False
        else: # string; compare against length
            is_input_case_string = True

    # get runtime and memory of each submission
    output_temp_list = []
    for token in submission_tokens_dict:
        code_input = submission_tokens_dict[token]
        if (output := code_compiler.get_submission_result(token)):
            output_temp_list.append([code_input, output[0], output[1]])
    
    # estimate time complexity and return the best fitting model
    if is_input_case_string:
        x_data = [len(i[0]) for i in output_temp_list]
    else:
        x_data = [i[0] for i in output_temp_list]
    runtime_list = [i[1] for i in output_temp_list]

    out = model_fitting.get_complexity_estimates(x_data, runtime_list)
    return out
   