#libraries to make the rest api work
from flask import Flask
from flask_restful import Api, Resource
import json

#libraries to make sphere engine work
from sphere_engine import CompilersClientV4
from sphere_engine.exceptions import SphereEngineException
from time import sleep

#libraries for graph fitting
import numpy as np
from scipy.optimize import curve_fit
#######################################################
"""
naming convention:
methods = snake_case
variables = camelCase
"""

app = Flask(__name__)
api = Api(app)

@app.route("/")
def home():
    return "Hello, World!"


#a class that extends "Resource" class 
class Complexity(Resource):
    def __init__(self):

        #to keep track of requests sent to Sphere engine API
        self.requestCounter = 0
        #points at the index of token currently being used
        self.tokenCounter = 0

        # Access token and endpoint for accessing the API
        self.allTokens = ['5cb67f444d05db8c8950aed82364ec60']
        self.accessToken = self.allTokens[self.tokenCounter]
        self.allEndpoints = ['8fd38a58.compilers.sphere-engine.com']
        self.endpoint = self.allEndpoints[self.tokenCounter]

    
    def sphere_connection_test(self):
        """Checks if the connection to sphere engine API is valid.
        
        Args: 
        accessToken: Sphere engine access token
        endpoint: Sphere engine endpoint
        """
        self.accessToken = self.allTokens[self.tokenCounter]
        client = CompilersClientV4(self, self.accessToken, self.endpoint)
        try:
            response = client.test()
            print(response)
        except SphereEngineException as e:
            if e.code == 401:
                print('Invalid access token')
    
    def get_compiler_ids(self):
        """Gets the compiler information that Sphere engine supports.
        Each language compiler has a unique ID.
        
        Args: 
        accessToken: Sphere engine access token
        endpoint: Sphere engine endpoint
        """
        self.accessToken = self.allTokens[self.tokenCounter]
        client = CompilersClientV4(self.accessToken, self.endpoint)
        try:
            response = client.compilers()
            allItems = response["items"]
            for i in range(len(allItems)):
                compilerID = allItems[i]["id"]
                compilerName = allItems[i]["name"]                
                print(f"compiler ID = {compilerID}, language = {compilerName}")
        except SphereEngineException as e:
            if e.code == 401:
                print('Invalid access token')

    def sphere_send_code(self, source, inputs, compilerID):
        """Sends the code and compiler id to the Sphere engine API.
        Gets a submission ID in return.
        
        Args: 
        accessToken: Sphere engine access token
        endpoint: Sphere engine endpoint
        source: Code for which the runtime has to be determined
        inputs: Input cases for the code (list of cases)
        compilerID: The ID of compiler, based on code langauge
        """
        self.accessToken = self.allTokens[self.tokenCounter]
        client = CompilersClientV4(self.accessToken, self.endpoint)
        compiler = compilerID
        try:
            #reset the list of submission ids
            submissionIDs = []
            #loop through all the inputs; add pause to avoid being marked as DOS
            for inp in inputs:
                self.requestCounter += 1
                print("processing input", self.requestCounter)
                print("inp = ", inp)
                #submission limit is 500; change token after 490
                if self.requestCounter==500:
                    self.requestCounter = 0
                    self.tokenCounter += 1
                    if self.tokenCounter>=10: #assuming 10 tokens in allTokens
                        #send an error by calling another function 
                        #exit this method
                        pass
                #send the code, compilerID and input to the API
                response = client.submissions.create(source, compiler, inp)
                submissionIDs.append(response["id"])
                #pause for 2 seconds
                sleep(1)
            print("\n\nsubmission IDs list: ", submissionIDs)
            return submissionIDs
        except SphereEngineException as e:
            if e.code == 401:
                print('Invalid access token')
            elif e.code == 402:
                print('Unable to create submission')
            elif e.code == 400:
                print('Error code: ' + str(e.error_code) + ', details available in the message: ' + str(e))

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
        except Exception as e:
            #send an error message if lang not found, handle in the get method
            compID = "ID not found error"
        return compID

    def sphere_run_time(self, idList):
        """Returns the runtime of each test case.

        Args: 
        idList: the list of ids returned by Sphere Engine for the test cases

        Returns:
        timeList = list of runtime for all test cases
        """
        # initialization
        client = CompilersClientV4(self.accessToken, self.endpoint)
        runtimeList = []
        # API usage
        try:
            for id in idList:
                #send one ID at a time
                response = client.submissions.getMulti(id)
                runtimeStatus = int(response["items"][0]["result"]["status"]["code"])
                runtime = response["items"][0]["result"]["time"]
                print(f"ID = {id}, status = {runtimeStatus}, runtime = {runtime}")
                #add wait time if the code has not completed execution yet
                while runtimeStatus in [0, 1, 2, 3]:
                    #the code execution has not completed yet
                    sleep(1)
                    response = client.submissions.getMulti(id)
                    runtimeStatus = int(response["items"][0]["result"]["status"]["code"])

                #only adding the runtime for successful executions
                sleep(1)
                if runtimeStatus==15:
                    runtime = float(response["items"][0]["result"]["time"])
                    #check if runtime is not None
                    if runtime:
                        print("added runtime: ", runtime)
                        runtimeList.append(runtime)
            return runtimeList

        except SphereEngineException as e:
            if e.code == 401:
                print('Invalid access token')
            elif e.code == 400:
                print('Error code: ' + str(e.error_code) + ', details available in the message: ' + str(e))
    
    def constant_model(self, x, a):
        """O(1)
        """
        return (0*x)+a
    
    def logarithmic_model(self, x, a, b):
        """O(log n)
        """
        return (a*np.log(x)) + b

    def linear_model(self, x, a, b):
        """O(n)
        """
        return (a*x)+b
        
    def quasilinear_model(self, x, a, b):
        """O(n*log n)
        """
        return (a*x*np.log(x)) + b

    def quadratic_model(self, x, a, b, c):
        """O(n^2)
        """
        return (a*x*x) + (b*x) + c

    def exponential_model(self, x, a, b):
        """O(2^n)
        """
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
        #get the best fit for each model
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

        
        complexityList = ["Constant", "Logarithmic", "Linear", "Quasilinear",
        "Quadratic", "Exponential"]
        errorList = np.array([constantError, logarithmicError, linearError,
        quasilinearError, quadraticError, exponentialError])
        lowestIndex = np.argmin(errorList)
        print("Error List is: ", errorList)
        print("lowest error: ", lowestIndex)
        
        return complexityList[lowestIndex]


    def get(self, code, test, lang):
        """
        Method description 
        """
        try:
            code = code.replace("%SLASH", "/")
            test = test.replace("%SLASH", "/")
            test = test.split("EnDoFtEsTcAsE")
            #removing the last empty element
            test = test[:-1]
            #print("\n\nreceived code: ", code)
            #print("\nreceived test: ", test, "\n\n")
            #print("\nreceived language: ", lang, "\n\n")
            #compiler ID lookup
            compID = self.compilerLookup(lang)
            if compID == "ID not found error":
                #send an error message
                print(compID)
                pass
            else:
                #send the request to sphere engine
                sphereSubmissionIDs = self.sphere_send_code(source=code, inputs=test, compilerID=compID)        
                #print("response from sphere = ", sphereSubmissionIDs)

                #get runtime
                self.runtimeList = self.sphere_run_time(sphereSubmissionIDs)
                #check if the runtime list is non empty 
                if len(self.runtimeList) == 0:
                    #the inputs did not successfully execute
                    errorString = "Oh no! The compiler was not able to execute your code.\n\
                    Please make sure your code does not have any errors and the test cases are not too computationally expensive.\n\
                    Contact the developer if the errors persist."
                    raise Exception(errorString)
                elif len(self.runtimeList)<4:
                    errorString = "The input cases are taking too long to execute.\n\
                        Please ensure that the test cases are not computationally too expensive and try again."
                    raise Exception(errorString)
                self.runtimeList = np.sort(self.runtimeList)
                print("runtimes: ", self.runtimeList)
                self.xData = np.array([i for i in range(1, len(self.runtimeList)+1, 1)])
                print("xData: ", self.xData)


                #get the model with the least error rate
                bestFittingModel = self.best_model()
                print("the best fitting model is: ", bestFittingModel)
                response = {"estimatedComplexity": bestFittingModel,
                "runtimeList": list(self.runtimeList),
                "constantModel": list(self.constantPars),
                "linearModel": list(self.linearPars),
                "logModel": list(self.logPars),
                "quasiModel": list(self.quasiPars),
                "quadraticModel": list(self.quadraticPars),
                "exponentialModel": list(self.exponentialPars)}
                #creating dictionaries that can be sent as response
                jsonDump = json.dumps(response)

                print(self.runtimeList, "\n\n")
                return jsonDump
        except Exception as e:
            return e



api.add_resource(Complexity, "/complexity/<string:code>/<string:test>/<string:lang>")

app.run(debug=False) 

# if __name__ == "__main__":
#     #change to flase when sending to sever
#     app.run(debug=False) 

