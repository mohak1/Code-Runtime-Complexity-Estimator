"""this is the entrypoint file"""
# standard library imports
from typing import List, Union
import functools
import logging

# external library imports
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

# internal imports
from app.models import website_data
from app.helpers import code_compiler, estimate_complexity
import app.settings as settings
from app.helpers import decorators

app = FastAPI(debug=settings.debug_state)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the filter
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.args[2] != "/healthy"

# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

@app.get('/')
@decorators.catchall_exceptions
def base_url():
    # include a list of the available endpoints
    endpoints = '`/healthy` `/get_active_languages` `/estimate_complexity`'
    return f'available endpoints are: {endpoints}'


@app.get('/test_discord_integration')
@decorators.catchall_exceptions
def raise_an_exception():
    raise Exception('discord integration test')

@app.get('/healthy')
@decorators.catchall_exceptions
def health_check():
    return True


@functools.lru_cache(maxsize=5)
@app.get('/get_active_languages', status_code=status.HTTP_200_OK)
@decorators.catchall_exceptions
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
@decorators.catchall_exceptions
# decorator for catch-all exceptions
def estimate_code_complexity(
        data: website_data.CodeSubmissions,
        response: Response
    ) -> Union[dict, str]:
    # gether inputs for the code
    if not (input_list := code_compiler.generate_inputs_for_code(data)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "`input_type` value not recognised"

    # submit inputs to the compiler
    submission_tokens_dict = code_compiler.get_submission_tokens_dict(
        code=data.code,
        language_id=data.language_id,
        input_list=input_list,
    )

    # get runtime of each submission
    is_error, outputs = code_compiler.get_runtimes_from_tokens(
        submission_tokens_dict
    )
    if is_error:
        # send one of the compiler errors
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'error': outputs}
    
    # estimate time complexity and return the best fitting model
    return estimate_complexity.get_complexity_estimates(
        input_and_time_list=outputs,
        input_type=data.input_type
    )
