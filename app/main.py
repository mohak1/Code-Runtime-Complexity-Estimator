"""this is the entrypoint file"""
# standard library imports
from typing import List, Union
import functools

# external library imports
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

# internal imports
from app.models import website_data
from app.helpers import code_compiler, model_fitting

app = FastAPI(debug=True)

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
    endpoints = '`/healthy` `/get_active_languages` `/estimate_complexity`'
    return f'available endpoints are: {endpoints}'

@app.get('/healthy')
def health_check():
    return True

@functools.lru_cache(maxsize=5)
@app.get('/get_active_languages', status_code=status.HTTP_200_OK)
def programming_languages(response: Response) -> Union[List, None]:
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
def estimate_complexity(
        data: website_data.CodeSubmissions,
        response: Response
    ) -> Union[dict, str]:
    # gether inputs for the code
    if not (input_list := code_compiler.generate_inputs_for_code(data)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "`input_type` value not recognised"
    
    # submit inputs to the compiler
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

    # get runtime and memory of each submission
    output_temp_list = []
    for token in submission_tokens_dict:
        code_input = submission_tokens_dict[token]
        if (output := code_compiler.get_submission_result(token)):
            output_temp_list.append([code_input, output])
    # return an error if output_temp_list is empty
    if not output_temp_list:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return "an error occured while compiling the code"
    # estimate time complexity and return the best fitting model
    if is_input_case_string:
        x_data = [len(i[0]) for i in output_temp_list]
    else:
        x_data = [i[0] for i in output_temp_list]
    runtime_list = [i[1] for i in output_temp_list]
    out = model_fitting.get_complexity_estimates(x_data, runtime_list)
    return out
   