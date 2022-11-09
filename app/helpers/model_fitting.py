import json
from typing import List, Union

import scipy
import numpy as np

from app.helpers import complexity_models

def get_mean_squared_error(
    outputs_of_model: List[float], actual_runtimes: List[float]
) -> List[float]:
    return (sum((outputs_of_model - actual_runtimes)**2))/len(actual_runtimes)

def get_complexity_estimates(
    x_data: List[Union[int, float]], runtime_list: List[float]
) -> json:
    # get the arguments for each model that fit the curve best
    #constant model
    constant_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.constant_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0]
    )
    constant_output = complexity_models.constant_model(x_data, *constant_args)
    constant_error = get_mean_squared_error(constant_output, runtime_list)
    
    #logarithmic model
    log_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.logarithmic_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    logarithmic_output = complexity_models.logarithmic_model(x_data, *log_args)
    logarithmic_error = get_mean_squared_error(logarithmic_output, runtime_list)
    
    #linear model
    linear_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.linear_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    linear_output = complexity_models.linear_model(x_data, *linear_args)
    linear_error = get_mean_squared_error(linear_output, runtime_list)
    
    #quasilinear model
    quasi_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.quasilinear_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    quasilinear_output = complexity_models.quasilinear_model(
        x_data, *quasi_args
    )
    quasilinear_error = get_mean_squared_error(quasilinear_output, runtime_list)
    
    #quadratic model
    quadratic_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.quadratic_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0,0]
    )
    quadratic_output = complexity_models.quadratic_model(
        x_data, *quadratic_args
    )
    quadratic_error = get_mean_squared_error(quadratic_output, runtime_list)
    
    #exponential model
    exponential_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.exponential_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    exponential_output = complexity_models.exponential_model(
        x_data, *exponential_args
    )
    exponential_error = get_mean_squared_error(exponential_output, runtime_list)
    
    # get the name of the least complexity model
    complexityList = [
        "Constant", "Logarithmic", "Linear", "Quasilinear",
        "Quadratic", "Exponential"
    ]
    error_list = np.array([
        constant_error, logarithmic_error, linear_error, quasilinear_error,
        quadratic_error, exponential_error
    ])
    index_of_lowest_error = np.argmin(error_list)
    best_fitting_model = complexityList[index_of_lowest_error]
    
    return {
        'estimatedComplexity': best_fitting_model,
        'runtime_list': list(runtime_list),
        'constant_model': list(constant_args),
        'linear_model': list(linear_args),
        'log_model': list(log_args),
        'quasi_model': list(quasi_args),
        'quadratic_model': list(quadratic_args),
        'exponential_model': list(exponential_args)
    }
