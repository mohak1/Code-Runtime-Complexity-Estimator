import scipy
import numpy as np
from typing import List, Union
import json
from helpers import complexity_models

def get_mean_squared_error(
    outputs_of_model: List[float], actual_runtimes: List[float]
) -> List[float]:
    return (sum((outputs_of_model - actual_runtimes)**2))/len(actual_runtimes)

def get_complexity_estimates(
    x_data: List[Union[int, float]], runtime_list: List[float]
) -> json:
    #constant
    constant_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.constant_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0]
    )
    constantOutput = complexity_models.constant_model(x_data, *constant_args)
    constantError = get_mean_squared_error(constantOutput, runtime_list)
    
    #logarithmic
    log_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.logarithmic_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    logarithmicOutput = complexity_models.logarithmic_model(x_data, *log_args)
    logarithmicError = get_mean_squared_error(logarithmicOutput, runtime_list)
    
    #linear
    linear_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.linear_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    linearOutput = complexity_models.linear_model(x_data, *linear_args)
    linearError = get_mean_squared_error(linearOutput, runtime_list)
    
    #quasilinear
    quasi_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.quasilinear_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    quasilinearOutput = complexity_models.quasilinear_model(
        x_data, *quasi_args
    )
    quasilinearError = get_mean_squared_error(quasilinearOutput, runtime_list)
    
    #quadratic
    quadratic_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.quadratic_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0,0]
    )
    quadraticOutput = complexity_models.quadratic_model(
        x_data, *quadratic_args
    )
    quadraticError = get_mean_squared_error(quadraticOutput, runtime_list)
    
    #exponential
    exponential_args, _ = scipy.optimize.curve_fit(
        f=complexity_models.exponential_model, method="lm", xdata=x_data,
        ydata=runtime_list, p0=[0,0]
    )
    exponentialOutput = complexity_models.exponential_model(
        x_data, *exponential_args
    )
    exponentialError = get_mean_squared_error(exponentialOutput, runtime_list)
    
    #least error model
    complexityList = [
        "Constant", "Logarithmic", "Linear", "Quasilinear",
        "Quadratic", "Exponential"
    ]
    errorList = np.array([
        constantError, logarithmicError, linearError, quasilinearError,
        quadraticError, exponentialError
    ])
    lowestIndex = np.argmin(errorList)
    best_fitting_model = complexityList[lowestIndex]
    
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
