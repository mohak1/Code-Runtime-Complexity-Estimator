import base64
import string
import random
from typing import List, Union
import settings
from models import website_data

def get_string_input_sample_pool(allowed_char_code: str):
    """
    allowed_char_code str contains on/off flags
    allowed_char_code[0] -> are lowercase alphabets allowed
    allowed_char_code[1] -> are uppercase alphabets allowed
    allowed_char_code[2] -> are integers allowed
    """
    sample_pool = []
    if allowed_char_code[0]:
        sample_pool.append(string.ascii_uppercase)
    if allowed_char_code[1]:
        sample_pool.append(string.ascii_lowercase)
    if allowed_char_code[2]:
        sample_pool.append(string.digits)
    return ''.join(sample_pool)


def generate_string_inputs(
    str_info: website_data.CodeSubmissionStringDetails,
    num_inputs: int,
) -> List[str]:

    sample_pool = get_string_input_sample_pool(str_info.characters_allowed)
    if str_info.max_length <= num_inputs:
        step = 1
    else:
        # generate num_inputs inputs starting size 1
        step = str_info.max_length // num_inputs
    inputs_list = []
    for i in range(1, str_info.max_length, step):
        item = ''.join([random.choice(sample_pool) for _ in range(i)])
        inputs_list.append(item)
    return inputs_list


def generate_number_inputs(
    num_info: website_data.CodeSubmissionNumberDetails,
    num_inputs: int,
) -> List[Union[int, float]]:
    if num_info.range_end - num_info.range_start <= num_inputs:
        step = 1
    else:
        step = (num_info.range_end - num_info.range_start) / num_inputs
        if num_info.numbers_allowed not in settings.FLOAT_ALLOWED_CODES_LIST:
            step = int(round(step, 0))
    input_list = []
    num = num_info.range_start
    while num <= num_info.range_end:
        input_list.append(num)
        num += step
    return input_list
