# standard library imports
import json
from typing import List, Tuple
import logging

# external library imports
import scipy
import numpy as np

# internal imports
from app.helpers import complexity_models
import app.settings as settings

def get_standard_error(
    outputs_of_model: np.array, actual_runtimes: List[float]
) -> List[float]:
    diff = outputs_of_model - actual_runtimes
    return np.std(diff)/np.sqrt(len(diff))

def min_max_normalise(data: List[float]) -> List[float]:
    data = np.array(data)
    min_nax_norm = (data-data.min()) / (data.max()-data.min()+0.00001)
    return min_nax_norm.tolist()

def prepare_data_for_complexity_estimation(
    input_and_time_list: List[Tuple[str, str]],
    input_type: str,
) -> Tuple[List[int], List[float]]:
    if input_type == settings.STRING_INPUT_CODE:
        x_data = [len(i[0]) for i in input_and_time_list]
    else:
        x_data = [i[0] for i in input_and_time_list]
    runtime_list = [i[1] for i in input_and_time_list]
    normalised_runtime_list = min_max_normalise(runtime_list)
    return x_data, normalised_runtime_list

def get_complexity_estimates(
    input_and_time_list: List[Tuple[str, str]],
    input_type: str,
) -> json:
    x_data, runtime_list = prepare_data_for_complexity_estimation(
        input_and_time_list, input_type
    )
    # get the arguments for each model that fit the curve best
    #constant model
    try:
        constant_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.constant_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'constant parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            constant_args = [runtime_list[0]]
        else:
            raise RuntimeError(e)

    constant_output = complexity_models.constant_model(x_data, *constant_args)
    constant_error = get_standard_error(constant_output, runtime_list)
    
    #logarithmic model
    try:
        log_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.logarithmic_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0,0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'log parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            log_args = [runtime_list[0],runtime_list[0]]
        else:
            raise RuntimeError(e)

    logarithmic_output = complexity_models.logarithmic_model(x_data, *log_args)
    logarithmic_error = get_standard_error(logarithmic_output, runtime_list)
    
    #linear model
    try:
        linear_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.linear_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0,0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'linear parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            linear_args = [runtime_list[0],runtime_list[0]]
        else:
            raise RuntimeError(e)

    linear_output = complexity_models.linear_model(x_data, *linear_args)
    linear_error = get_standard_error(linear_output, runtime_list)
    
    #quasilinear model
    try:
        quasi_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.quasilinear_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0,0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'quasi parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            quasi_args = [runtime_list[0],runtime_list[0]]
        else:
            raise RuntimeError(e)

    quasilinear_output = complexity_models.quasilinear_model(
        x_data, *quasi_args
    )
    quasilinear_error = get_standard_error(quasilinear_output, runtime_list)
    
    #quadratic model
    try:
        quadratic_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.quadratic_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0,0,0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'quadratic parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            quadratic_args = [runtime_list[0],runtime_list[0],runtime_list[0]]
        else:
            raise RuntimeError(e)

    quadratic_output = complexity_models.quadratic_model(
        x_data, *quadratic_args
    )
    quadratic_error = get_standard_error(quadratic_output, runtime_list)
    
    #exponential model
    try:
        exponential_args, _ = scipy.optimize.curve_fit(
            f=complexity_models.exponential_model, method="lm", xdata=x_data,
            ydata=runtime_list, p0=[0,0]
        )
    except RuntimeError as e:
        if 'Optimal parameters not found' in e.args[0]:
            logging.debug(
                f'exponential parameters not found for points. Error trace: {e} '
                f'x_data={x_data}\nruntime_list={runtime_list}'
            )
            exponential_args = [runtime_list[0],runtime_list[0]]
        else:
            raise RuntimeError(e)

    exponential_output = complexity_models.exponential_model(
        x_data, *exponential_args
    )
    exponential_error = get_standard_error(exponential_output, runtime_list)
    
    # get the name of the least complexity model
    complexity_list = [
        "Constant", "Logarithmic", "Linear", "Quasilinear",
        "Quadratic", "Exponential"
    ]
    error_list = np.array([
        constant_error, logarithmic_error, linear_error, quasilinear_error,
        quadratic_error, exponential_error
    ])
    index_of_lowest_error = np.argmin(error_list)
    best_fitting_model = complexity_list[index_of_lowest_error]
    
    return {
        'estimated_complexity': best_fitting_model,
        'runtime_list': list(runtime_list),
        'constant_model': list(constant_args),
        'linear_model': list(linear_args),
        'log_model': list(log_args),
        'quasi_model': list(quasi_args),
        'quadratic_model': list(quadratic_args),
        'exponential_model': list(exponential_args)
    }
