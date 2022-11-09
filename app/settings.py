import os

MAX_INPUTS = 100    # num inputs to generate
FLOAT_ALLOWED_CODES_LIST = ['01', '11']   # is float allowed
FLOAT_ALLOWED_CODE = '01'
INT_ALLOWED_CODE = '10'

inside_docker = os.getenv('is_dockerised', False)
if inside_docker:
    COMPILER_BASE_URL = 'http://judge0-server-1:2358'
else:
    COMPILER_BASE_URL = 'http://localhost:2358'