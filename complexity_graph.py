#libraries for rest api
from flask import Flask
from scipy.sparse.sputils import isdense
from flask_restful import Api, Resource
from flask_cors import CORS
import json

#libraries for graph fitting
import numpy as np
from scipy.optimize import curve_fit

"""
naming conventions:
methods = snake_case
variables = camelCase
Speech marks = double unless necessary
"""

app = Flask(__name__)
CORS(app)
app.config['Access-Control-Allow-Origin'] = '*'
api = Api(app)

@app.route("/")
def home():
    #To test if the server works
    return "Hello, World!"


class Complexity(Resource):
    def __init__(self):
        pass

    def constant_model(self, x, a):
        """Model to represent constant runtime
        O(1)"""
        return (0*x)+a

    def logarithmic_model(self, x, a, b):
        """Model to represent logarithmic runtime
        O(log n)"""
        return (a*np.log(x)) + b

    def linear_model(self, x, a, b):
        """Model to represent linear runtime
        O(n)"""
        return (a*x)+b

    def quasilinear_model(self, x, a, b):
        """Model to represent quasilinear runtime
        O(n*log n)"""
        return (a*x*np.log(x)) + b

    def quadratic_model(self, x, a, b, c):
        """Model to represent quadratic runtime
        O(n^2)"""
        return (a*x*x) + (b*x) + c

    def exponential_model(self, x, a, b):
        """Model to represent exponential runtime
        O(2^n)"""
        return 2**((a*x)+b)

    def get_MSE(self, yModel, yData):
        """
        Args:
        yModel: npArray containing the model outputs
        yData: npArray of algorithm runtime

        Returns:
        mse: The error rate
        """
        mse = sum((yModel-yData)**2)
        return mse

    def best_model(self):
        """
        Fits the complexity models to the runtimes and determines the best fitting
        model by computing ht error rate. 

        Returns:
        bestModel: The model with the least error on the runtimes
        """
        try: 
            #constant
            self.constantPars, cov = curve_fit(f=self.constant_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0])
            constantOutput = self.constant_model(self.xData, *self.constantPars)
            constantError = self.get_MSE(constantOutput, self.runtimeList)
            #logarithmic
            self.logPars, cov = curve_fit(f=self.logarithmic_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0,0])
            logarithmicOutput = self.logarithmic_model(self.xData, *self.logPars)
            logarithmicError = self.get_MSE(logarithmicOutput, self.runtimeList)
            #linear
            self.linearPars, cov = curve_fit(f=self.linear_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0,0])
            linearOutput = self.linear_model(self.xData, *self.linearPars)
            linearError = self.get_MSE(linearOutput, self.runtimeList)
            #quasilinear
            self.quasiPars, cov = curve_fit(f=self.quasilinear_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0,0])
            quasilinearOutput = self.quasilinear_model(self.xData, *self.quasiPars)
            quasilinearError = self.get_MSE(quasilinearOutput, self.runtimeList)
            #quadratic
            self.quadraticPars, cov = curve_fit(f=self.quadratic_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0,0,0])
            quadraticOutput = self.quadratic_model(self.xData, *self.quadraticPars)
            quadraticError = self.get_MSE(quadraticOutput, self.runtimeList)
            #exponential
            self.exponentialPars, cov = curve_fit(f=self.exponential_model, method="lm",
            xdata=self.xData, ydata=self.runtimeList, p0=[0,0])
            exponentialOutput = self.exponential_model(self.xData, *self.exponentialPars)
            exponentialError = self.get_MSE(exponentialOutput, self.runtimeList)
            #least error model
            complexityList = ["Constant", "Logarithmic", "Linear", "Quasilinear",
            "Quadratic", "Exponential"]
            errorList = np.array([constantError, logarithmicError, linearError,
            quasilinearError, quadraticError, exponentialError])
            lowestIndex = np.argmin(errorList)
            bestModel = complexityList[lowestIndex]
            return bestModel
        except Exception as e:
            self.isError=1
            error = "An error occured while determining the best fitting model.\n"
            self.errorMessage = error + str(e)

    def get(self, code, test, lang):

        """
        The driver method of the API. It listens to the server requests, sends
        data to Sphere API and determines the best fittings models using helper 
        methods.

        Args:
        code: The source code for which the runtime has to be determined 
        test: The list of test cases that the user has provided to determine the runtime
        lang: The language in which the code is written (provided by the user)

        Returns:
        jsonDump: A JSON formatted dictionary contatining the best fitting model, 
        the runtime list and the paramters for each model
        OR
        jsonError: A JSON formatted dictionary of error encountered during the 
        process of determining the best model 
        """
        #reset the error flag and the error message
        self.isError = 0
        self.errorMessage = ""
        try:
            code = code.replace("%SLASH", "/")
            test = test.replace("%SLASH", "/")
            test = test.split("EnDoFtEsTcAsE")
            #removing the last empty element
            test = test[:-1]          
            compID = self.compilerLookup(lang)
            #raise an error if compiler lookup is unsuccessful
            if self.isError==1:
                raise Exception(self.errorMessage)

            sphereSubmissionIDs = self.sphere_send_code(source=code, inputs=test, compilerID=compID)
            #raise an error if sending code is unsuccessful
            if self.isError==1:
                raise Exception(self.errorMessage)
            
            self.runtimeList = self.sphere_run_time(sphereSubmissionIDs)
            if len(self.runtimeList) == 0:
                #the inputs did not successfully execute
                if self.isError==1:
                    #an error occured during the process
                    raise Exception()
                else:
                    errorString = "Oh no! The compiler was not able to determine \
                        the runtime of your code (and input cases).\n\
                        Please make sure your code does not have any errors \
                        and the test cases are not too computationally expensive.\n\
                        Contact the developer if the error persist."
                    raise Exception(errorString)
            elif len(self.runtimeList)<4:
                errorString = "The input cases took too long to execute.\n\
                    Please ensure that the test cases are not too computationally \
                    expensive and try again."
                raise Exception(errorString)
            #arrange the runtimes in an incrasing order
            self.runtimeList = np.sort(self.runtimeList)
            self.xData = np.array([i for i in range(1, len(self.runtimeList)+1, 1)])
            bestFittingModel = self.best_model()
            #check if this process returned an error
            if self.isError==1:
                raise Exception()
            
            response = {"estimatedComplexity": bestFittingModel,
            "runtimeList": list(self.runtimeList),
            "constantModel": list(self.constantPars),
            "linearModel": list(self.linearPars),
            "logModel": list(self.logPars),
            "quasiModel": list(self.quasiPars),
            "quadraticModel": list(self.quadraticPars),
            "exponentialModel": list(self.exponentialPars)}
            
            jsonDump = json.dumps(response)
            return jsonDump
        
        except Exception as e:
            error = {
                "errorMessage" : self.errorMessage
            }
            jsonError = json.dumps(error)
            return jsonError

api.add_resource(Complexity, "/complexity/<string:code>/<string:test>/<string:lang>")

if __name__ == "__main__":
    app.run(debug=False)
