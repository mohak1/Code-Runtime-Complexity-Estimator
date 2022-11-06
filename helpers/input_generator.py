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



def generate_array_inputs(
    arr_info: website_data.CodeSubmissionArrayDetails,
    num_inputs: int,
) -> List[Union[int, float, str]]:
    if arr_info.element_type == 0:  # integer
        int_details = website_data.CodeSubmissionNumberDetails(
            numbers_allowed=settings.INT_ALLOWED_CODE,
            range_start=arr_info.range_start,
            range_end=arr_info.range_end
        )
        return generate_number_inputs(
            num_info=int_details, num_inputs=num_inputs
        )
    
    elif arr_info.element_type == 1:    # float
        float_model = website_data.CodeSubmissionNumberDetails(
            numbers_allowed=settings.FLOAT_ALLOWED_CODE,
            range_start=arr_info.range_start,
            range_end=arr_info.range_end
        )
        return generate_number_inputs(
            num_info=float_model, num_inputs=num_inputs
        )
    
    elif arr_info.element_type == 2:    # string
        str_model = website_data.CodeSubmissionStringDetails(
            characters_allowed = arr_info.characters_allowed,
            max_length = arr_info.max_length
        )
        return generate_string_inputs(
            str_info = str_model, num_inputs=num_inputs
        )

    else:
        raise # array 'elements_type' not recognised exception
