#libraries for rest api
from flask import Flask
from scipy.sparse.sputils import isdense
from flask_restful import Api, Resource
from flask_cors import CORS
import json

#libraries to make sphere engine work
from sphere_engine import CompilersClientV4
from sphere_engine.exceptions import SphereEngineException
from time import sleep

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

#app = Flask(__name__)
#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def home():
    #To test if the server works
    return "Hello, World!"


class Complexity(Resource):
    def __init__(self):
        """Initializes the shared variables for Sphere API connection, error flag
        and error messages.
        """
        #self.accessToken = "5cb67f444d05db8c8950aed82364ec60" #espired
        #self.endpoint = "8fd38a58.compilers.sphere-engine.com" #expired

        self.accessToken = "8c746e2f0d6f0c40f9fcf0124ee939d9" #espires on 4th of Aug 
        self.endpoint = "443a014d.compilers.sphere-engine.com" #expires on 4th of Aug

        self.isError = 0
        self.errorMessage = ""

    def sphere_connection_test(self):
        """Checks if the connection to sphere engine API is valid.

        Args:
        accessToken: Sphere engine access token
        endpoint: Sphere engine endpoint
        """
        client = CompilersClientV4(self.accessToken, self.endpoint)
        try:
            response = client.test()
        except SphereEngineException as e:
            self.isError = 1
            if e.code == 401:
                print("Invalid access token")
            self.errorMessage = str(e)
        except Exception as e:
            self.isError=1
            self.errorMessage = str(e)

    def get_compiler_ids(self):
        """Gets the compiler information that Sphere engine supports.
        Each language compiler has a unique ID.
        """
        client = CompilersClientV4(self.accessToken, self.endpoint)
        try:
            response = client.compilers()
            allItems = response["items"]
            for i in range(len(allItems)):
                compilerID = allItems[i]["id"]
                compilerName = allItems[i]["name"]
                print(f"compiler ID = {compilerID}, language = {compilerName}")
        except SphereEngineException as e:
            self.isError = 1
            if e.code == 401:
                print("Invalid access token")
            self.errorMessage = str(e)
        except Exception as e:
            self.isError = 1
            self.errorMessage = str(e)

    def sphere_send_code(self, source, inputs, compilerID):
        """Sends the code and compiler id to the Sphere engine API.
        Gets a submission ID in return.

        Args:
        source: Source code for which the runtime has to be determined
        inputs: Input cases for the code (list of cases)
        compilerID: The ID of compiler, based on code langauge
        
        Returns:
        submissionIDs: A list of submission IDs returned by Sphere API
        """
        client = CompilersClientV4(self.accessToken, self.endpoint)
        compiler = compilerID
        try:
            submissionIDs = []
            for inp in inputs:
                response = client.submissions.create(source, compiler, inp)
                submissionIDs.append(response["id"])
                #pause for a second to avoid being marked as DOS
                sleep(1)
            return submissionIDs
        except SphereEngineException as e:
            self.isError = 1
            if e.code == 401:
                error = "Invalid access token"
            elif e.code == 402:
                error = "Unable to create submission" 
            elif e.code == 400:
                error = "Error code: " + str(e.error_code) + ", details available in the message: " + str(e)
            self.errorMessage = error
        except Exception as e:
            self.isError = 1
            error = "Error in sending request to Sphere API: " + str(e)
            self.errorMessage = error
 
    def compilerLookup(self, lang):
        """Looks up and returns  the compiler ID of the language from the compilerIDList dict.
        Dictionary key-value pairs obtained from the get_compiler_ids() method
        
        Args:
        lang: The langauge for which the compiler ID is to be returned

        Returns:
        CompID: The compiler ID of the requested language
        """
        compilerIDList = {
            "C" : 11,
            "C# [Mono]" : 27,
            "C++ [GCC]" : 1,
            "C++14 [GCC]" : 44,
            "Go" : 114,
            "Java": 10,
            "JavaScript [Rhino]" : 35,
            "JavaScript [SpiderMonkey]" : 112,
            "Node.js" : 56,
            "Objective-C" : 43,
            "Python 2.x [Pypy]" : 4,
            "Python 3.x" : 116,
            "R" : 117,
            "Rust" : 93,
            "Swift" : 85
        }
        try:
            compID = compilerIDList[lang]
            return compID
        except Exception as e:
            self.isError = 1
            error = "ID not found error: " + str(e)
            self.errorMessage = error

    def sphere_run_time(self, idList):
        """Returns the runtime of each test case.

        Args:
        idList: the list of ids returned by Sphere Engine for the test cases

        Returns:
        runtimeList = list of runtime for all test cases
        """
        client = CompilersClientV4(self.accessToken, self.endpoint)
        runtimeList = []
        try:
            for id in idList:
                response = client.submissions.getMulti(id)
                runtimeStatus = int(response["items"][0]["result"]["status"]["code"])
                runtime = response["items"][0]["result"]["time"]
                #add wait time if the code has not completed execution yet
                while runtimeStatus in [0, 1, 2, 3]:
                    #code is still executing
                    sleep(1)
                    response = client.submissions.getMulti(id)
                    runtimeStatus = int(response["items"][0]["result"]["status"]["code"])
                sleep(1)
                #only adding runtime for successful executions
                if runtimeStatus==15:
                    runtime = float(response["items"][0]["result"]["time"])
                    #append if the runtime is not None
                    if runtime:
                        runtimeList.append(runtime)
            return runtimeList
        except SphereEngineException as e:
            self.isError = 1
            if e.code == 401:
                error = "Invalid access token" 
            elif e.code == 400:
                error = "Error code: " + str(e.error_code) + ", details available in the message: " + str(e)
            self.errorMessage = error
        except Exception as e:
            self.isError = 1
            error = "Error in getting runtime from Sphere API: " + str(e)
            self.errorMessage = error

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
        print("\ninside get\n")
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
            #adding header
            jsonDump.headers.add("Access-Control-Allow-Origin", "*")
            return jsonDump
        
        except Exception as e:
            error = {
                "errorMessage" : self.errorMessage
            }
            jsonError = json.dumps(error)
            #adding header
            jsonDump.headers.add("Access-Control-Allow-Origin", "*")
            return jsonError

api.add_resource(Complexity, "/complexity/<string:code>/<string:test>/<string:lang>")

if __name__ == "__main__":
    app.run(debug=False)
