import numpy as np
from typing import List

def constant_model(x: List, a: float) -> np.array:
    # y = 0(x) + a
    return np.zeros(len(x)) + a

def logarithmic_model(x: List, a: float, b: float) -> np.array:
    # y = a(logx) + b
    x = np.array(x)
    x[x==0] = 1 # replace 0 by 1 since log(0) is inf
    return (a*np.log(x)) + b

def linear_model(x: List, a: float, b: float) -> np.array:
    # y = a(x) + b
    return (a*np.array(x))+b

def quasilinear_model(x: List, a: float, b: float) -> np.array:
    # y = a(x)(logx) + b
    x = np.array(x)
    return (a*x*x) + b

def quadratic_model(x: List, a: float, b: float, c: float) -> np.array:
    # y = a(x)(x) + b(x) + c
    x = np.array(x)
    return (a*x*x) + (b*x) + c

def exponential_model(x: List, a: float, b: float) -> np.array:
    # y = 2^(ax + b)
    x = np.array(x)
    return 2**((a*x)+b)
