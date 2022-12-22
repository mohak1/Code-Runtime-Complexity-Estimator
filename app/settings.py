# standard library imports
import os

MAX_INPUTS = 100    # num inputs to generate
FLOAT_ALLOWED_CODES_LIST = ['01', '11']   # is float allowed
FLOAT_ALLOWED_CODE = '01'
INT_ALLOWED_CODE = '10'
STRING_INPUT_CODE = '0'
COMPILER_BASE_URL = 'http://0.0.0.0:2358'

inside_docker = os.getenv('is_dockerised', False)
if inside_docker:
    debug_state = False # no debug for deployed app
else:
    debug_state = True
