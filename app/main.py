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
from app.helpers import notifs

app = FastAPI(debug=settings.debug_state)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGIN_LIST,
    allow_methods=['GET', 'POST'],
    allow_headers=["*"],
)

# Define the filter
class HealthyEndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return '/healthy' not in record.args

# Add filter to the logger
logging.getLogger("uvicorn.access").addFilter(HealthyEndpointFilter())


@app.get('/')
@decorators.catchall_exceptions
def base_url() -> str:
    # include a list of the available endpoints
    endpoints = '`/healthy` `/get_active_languages` `/estimate_complexity`'
    return f'available endpoints are: {endpoints}'


@app.get('/healthy')
@decorators.catchall_exceptions
def health_check() -> bool:
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
    notifs.send_message_on_discord(
        message="compiler didn't return the active languages list"
    )
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return None


@app.post('/estimate_complexity', status_code=200)
@decorators.async_catchall_exceptions
async def estimate_code_complexity(
        data: website_data.CodeSubmissions,
        response: Response
    ) -> Union[dict, str]:
    # gether inputs for the code
    if not (input_list := code_compiler.generate_inputs_for_code(data)):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "`input_type` value not recognised"

    # submit inputs to the compiler
    if not (submission_tokens_dict:=await code_compiler.get_submission_tokens_dict(
        code=data.code,
        language_id=data.language_id,
        input_list=input_list,
    )):
        # no submission ids - failed to make submissions in compiler
        logging.error(
            'got empty submissions tokens dict; args:\n'
            f'code={data.code}\nlanguage_id={data.language_id}\n'
            f'inputs={input_list}'
        )
        raise Exception('empty submission tokens dict returned')

    # get runtime of each submission
    is_error, outputs = await code_compiler.get_runtimes_from_tokens(
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
