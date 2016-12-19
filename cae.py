#!/usr/bin/env python2
# coding=utf-8
import os
import subprocess
import sys

import operator
import platform

import collections
import requests
import csv
from clint.arguments import Args
from clint.textui import puts, colored

commandExample = "Command example: \"cae 576 /test/main.exe 1,2,3\"\nLast argument is optional and can be in formats: \"1,2,3\" \"3-7\" \"2..5\", tests all if left blank."
noPathGiven = "No path given. Please enter path to the testing file!"
noPathExists = "Given path does not exist!"
notAFile = "Given path is not a file or an executable!"
fileValid = "File is valid!"
firstArgumentInvalid = "First argument must be the problem id!"
connectionError = "Connection error!"
invalidProblemId = "Invalid problem Id! (Error 404)"
problemIdOk = "Problem id OK!"
encodingISO = 'ISO-8859-1'
encodingUTF8 = 'utf_8'


class CLI():

    class Strings:
        NO_TOKEN_FOUND = "In order to know we're going to need your token. You can get one at https://codeassign.com/tokens"
        INPUT_TOKEN = "Please input your token: "

    class Endpoints(object):
        POST_EVALUATE = "https://api.codeassign.com/Evaluate/"

        @classmethod
        def get_evaluation_endpoint(cls, problem_id, token):
            return cls.POST_EVALUATE + str(problem_id) + "?token=" + token

    class Properties:
        KEY_TOKEN = "APP_TOKEN"
        KEY_LOG = "LOG"

        DEFAULT_PROPERTIES_FILE = ".codeassign"

        propertiesFilePath = os.path.join(os.path.expanduser("~"), ".codeassign")
        properties = dict()

        def __init__(self, properties_file_path=propertiesFilePath):
            self.propertiesFilePath = properties_file_path
            self.properties = dict([(row[0], row[1]) for row in csv.reader(open(properties_file_path, 'r'), delimiter='=')])

        def get_token(self):
            return self.properties.get(self.KEY_TOKEN, None)

        def set_token(self, token):
            self.properties[self.KEY_TOKEN] = token

        def get_log(self):
            return self.properties.get(self.KEY_LOG, 'False') == 'True'

        def set_log(self, log):
            self.properties[self.KEY_LOG] = log

        def is_token_present(self):
            return self.get_token() is not None

        def to_output(self):
            return "\n".join([k + '=' + v for k, v in self.properties.iteritems()])

        def save(self, output_file=propertiesFilePath):
            with open(output_file, 'w') as output:
                output.write(self.to_output())


    def __init__(self):

        # sys.path.insert(0, os.path.abspath('..'))

        # List of ints, used if user wants to test specific test cases (not all)
        self.testCases = []
        # GET problem path
        self.pathGetProblem = 'https://api.codeassign.com/Problem/'
        # GET TestCase values
        self.pathGetTestValues = 'https://api.codeassign.com/TestCase/'
        # POST AssociateConsoleToken
        self.pathAssociateToken = 'https://api.codeassign.com/AssociateConsoleToken/'

        # Path to .codeassign file
        self.tokenPath = os.path.join(os.path.expanduser("~"), ".codeassign")
        # Path to log file
        self.logFilePath = os.path.join(os.getcwd(), "cae_log.txt")

        # Problem id
        self.problemId = ''
        # Path to the user's exe file
        self.pathToExecutable = ''
        # File's extension
        self.fileType = ''
        # Internal list used to store the values from GET call
        self.values = []
        # Which compiler should be used
        self.compilerType = ''

        # List of outputs to evaluate
        self.outputList = []
        # Check if user wants more or less info
        self.showInfo = True
        # Additional options used in argument
        self.options = False
        # Wrote to log file
        self.logFileBool = False
        # First time log
        self.firstLog = True

        # Get all arguments from command line
        self.args = Args()
        self.checkIfNoArguments()

        # Check given arguments
        self.checkArguments()

        # Get test cases for given problem id
        self.values = self.getInputValues()

        # Load config file properties
        properties = CLI.Properties()

        token = self.load_token(properties)

        # Evaluate each test
        self.evaluate(self.problemId, token)

    def load_token(self, properties):
        if not properties.is_token_present():
            puts(colored.yellow(CLI.Strings.NO_TOKEN_FOUND))

            while True:
                token = self.request_token()
                if self.validate_token(token):
                    properties.set_token(token)
                    properties.save()
                    return token
        else:
            return properties.get_token()

    def request_token(self):
        sys.stdout.write(CLI.Strings.INPUT_TOKEN)
        return raw_input().rstrip()

    def validate_token(self, token):
        response = requests.post(self.pathAssociateToken + token)
        # Check if status not 200
        if response.status_code != requests.codes.ok:
            puts(colored.red("Bad request!2"))
            return False

        data = response.json()
        # Check if wrong token
        if 'errorMessage' in data.keys():
            puts(colored.red("Invalid token!"))
            return False

        # Modify encoding of account info
        self.modifyEncoding(data)

        # Token is ok
        if data['success'] and self.showInfo:
            puts(colored.green("Token is valid!\n"))
            formatNum = len(data['email'].decode('utf8')) + 8
            puts(" " * (formatNum / 3) + colored.yellow("Account info"))
            nameLen = len(data['name'].decode('utf8')) + 8
            puts("|" + "=" * formatNum + "|")

            puts("| " + colored.yellow("Name: ") + " " + data['name'] + " " * (
                formatNum - nameLen) + "|\n| " + colored.yellow(
                "Email: ") + data['email'] + "|")
            puts("|" + "=" * formatNum + "|")
            puts()
            return True

    # Test the code with input
    def evaluate(self, problem_id, token):
        for input in self.values:
            testCaseId = input['id']
            # Check which compiler to use based on the self.fileType
            self.setCompilerType()
            try:
                process = subprocess.Popen(self.compilerType, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, shell=False).communicate(input['input'])
                output = process[0]
                data = self.formatOutput(output, testCaseId)
                self.outputList.append(data)
            except OSError:
                puts(colored.red("ERROR! : Given file is not an executable! (Did you add the path of your compiler to PATH?)"))
                sys.exit(1)

        output = self.POSTEvaluate(problem_id, token)
        # Check if something is wrong
        self.checkJsonStatusCode(output)
        # Used to check if tests passed evaluation
        passed = 0
        # Used for checking how many tests were really tested (if user put too many)
        numberOfTests = 0

        # Dictionary of test cases
        testCaseDict = {}
        # Count used only for output log formatting
        count = 1
        # Another count ( yeah ) , for the right output number when there are only specific test cases, used for log
        countSpecificFile = 1
        # Dictionary keys
        i = 1
        
        # Write output log
        for testCase in output['testCases']:
            # Add new dictionary value, e.g. "1 : True"
            testCaseDict[i] = testCase['accepted']
            i += 1
            # Check if the output for this test case should be visible
            if not testCase['hiddenOutput']:
                # Write test status to log file if LOG=True(-more is given as a parameter)
                # If there are specific test cases
                if len(self.testCases) > 0:
                    if self.showInfo and (countSpecificFile in self.testCases):
                        self.writeLog(countSpecificFile, testCase)
                    countSpecificFile += 1
                else: # Write all test cases
                    if self.showInfo:
                        self.writeLog(count, testCase)
                        count += 1

        # Something was written to file
        if count > 1 or countSpecificFile > 0:
            self.logFileBool = True

        # Count specific, same as the above count, this one is used for command line output
        countSpecificOutput = 1

        # Check if there are specific test cases given by user
        if len(self.testCases) == 0:
            # Testing all available test cases
            for key in sorted(testCaseDict):
                numberOfTests += 1
                if self.checkTestCase(numberOfTests, testCaseDict[key]):
                    passed += 1
            puts()
        # Testing only specific test cases
        else:	
            for key in sorted(testCaseDict):
                if key in self.testCases:
                    numberOfTests += 1
                    if self.checkTestCase(countSpecificOutput, testCaseDict[key]):
                        passed += 1
                countSpecificOutput += 1
            puts()

        self.printFinalResult(output, passed, numberOfTests)

    def setCompilerType(self):
        if self.fileType == 'jar':
            self.compilerType = ['java', '-jar', self.pathToExecutable]
            return
        
        f = open(self.pathToExecutable, 'r')
        firstLine = f.readline()
        f.close()

        if platform.system() == 'Windows' or firstLine[:2] != '#!':
            if self.fileType == "py":
                self.compilerType = ['python', self.pathToExecutable]
            elif self.fileType == "rb":
                self.compilerType = ['ruby', self.pathToExecutable]
            else:
                self.compilerType = [self.pathToExecutable]
        else:
            self.compilerType = [self.pathToExecutable]

    def writeLog(self, count, testCase):
        # Used for formating
        separator = "=================================\n\n"
			
        # Format output for log file
        if testCase['accepted']:
            header = '>>>Test case number ' + str(count) + ": " + "Passed!<<<\nInput:\n"
        else:
            header = '>>>Test case number ' + str(count) + ": " + "Failed!<<<\n\nInput:\n"
        testCaseInput = testCase['input'].rstrip() + "\n\n"
        # Separator
        userOutputText = "Your output:\n"
        userOutput = testCase['userOutput'].rstrip() + "\n\n"
        reqOutputText = "Required output:\n"
        reqOutput = testCase['requiredOutput'].rstrip() + "\n\n"
        # Separator
        
        if self.firstLog:
            logFile = open(self.logFilePath, 'w')
            self.firstLog = False
        else:
            logFile = open(self.logFilePath, 'a')
        # Combine the formatted output
        fullLog = header + testCaseInput + separator + userOutputText + userOutput + reqOutputText + reqOutput + separator + "\n"
        logFile.write(fullLog)
        logFile.close()

    def POSTEvaluate(self, problem_id, token):
        return requests.post(CLI.Endpoints.get_evaluation_endpoint(problem_id, token), json=self.outputList).json()

    def formatOutput(self, output, testCaseId):
        data = {}
        data['id'] = testCaseId
        data['output'] = output
        return data

    def printFinalResult(self, output, passed, numberOfTests):
        # Given test cases dont exist
        if numberOfTests == 0 and len(self.testCases) > 0:
            puts(colored.red("Given test cases " + str(self.testCases) + " don't exist for problem with id " + str(
                self.problemId) + "!"))
            sys.exit(1)
        # No tests found
        elif numberOfTests == 0:
            puts(colored.red("No test cases found for problem with id " + str(self.problemId) + "!"))
            sys.exit(1)

        # Log was created and LOG=True(-more is used)
        if self.logFileBool and self.showInfo:
            puts(colored.yellow("Check log file \"cae_log\" in your working directory for more detailed info!"))

        # All tests passed
        if passed >= numberOfTests:
            puts(colored.green("\nAll (" + str(numberOfTests) + ") test/s passed! Well done!"))
        # All tests failed
        elif passed <= 0:
            puts(colored.red("\nAll (" + str(numberOfTests) + ") test/s failed! Try again!"))
        # Some test failed
        else:
            puts("\nNumber of tests passed: " + str(passed) + "/" + str(len(output['testCases'])))
            puts(colored.yellow("Some tests failed! Almost there, keep trying!"))

    def checkJsonStatusCode(self, output):
        if "statusCode" in output.keys():
            if output['statusCode'] == requests.codes.unauthorized:
                puts(colored.red("Invalid token!2"))
                sys.exit(1)
            elif output['statusCode'] != requests.codes.ok:
                puts(colored.red("Bad request!"))
                sys.exit(1)

    def checkTestCase(self, key, value):
        if value:
            puts('Test case number ' + str(key) + ": " + colored.green("Passed!"))
            return True
        else:
            puts('Test case number ' + str(key) + ": " + colored.red("Failed!"))
            return False

    # Get test cases for the given problemId
    def getInputValues(self):
        try:
            response = requests.get(self.pathGetTestValues + str(self.problemId))
            # Wrong problem id
            if not response.status_code == requests.codes.ok:
                puts(colored.red(invalidProblemId))
                sys.exit(1)
            else:
                # Show if user wants more info (LOG=True)
                if self.showInfo:
                    puts(colored.green(problemIdOk))
            response.encoding = "utf8"
            data = response.json()
            return data

        except requests.ConnectionError:
            puts(colored.red(connectionError))
            sys.exit(1)

    def checkArguments(self):
        # Check for additional options and modify internal values accordingly
        if "-" in self.args[len(self.args) - 1]:
            if self.args[-1] == "-less":
                self.modifyLog("\nLOG=False", False)
                self.options = True
            if self.args[-1] == "-more":
                self.modifyLog("\nLOG=True", True)
                self.options = True
        else:
            if os.path.exists(self.tokenPath) and os.path.isfile(self.tokenPath):
                tokenFile = open(self.tokenPath, 'r')
            else:
                tokenFile = open(self.tokenPath, 'w+')
            for i, line in enumerate(tokenFile):
                if i == 1:
                    value = line.split("=")[1].rstrip()
                    if value == "True":
                        self.showInfo = True
                    elif value == "False":
                        self.showInfo = False
                    else:
                        pass

        # Check if first argument(problemId) is a valid number
        try:
            self.problemId = int(self.args[0])
        except ValueError:
            #  Help command entered
            if self.args[0] == "help":
                puts(colored.yellow(commandExample))
            # Invalid input
            else:
                puts(colored.red(firstArgumentInvalid))
            sys.exit(1)

        # Check if second argument(executable) is a valid file
        if self.args[1]:
            pathToFile = self.getFullPath(self.args[1])
            self.getFileType(pathToFile)
            if pathToFile:
                if os.path.exists(pathToFile):
                    if os.path.isfile(pathToFile) and os.access(pathToFile, os.X_OK):
                        # Show if user wants more info (LOG=True)
                        if self.showInfo:
                            puts(colored.green(fileValid))
                        self.pathToExecutable = pathToFile
                    else:
                        puts(colored.red(notAFile))
                        puts(colored.yellow(commandExample))
                        sys.exit(1)
                else:
                    puts(colored.red(noPathExists))
                    puts(colored.yellow(commandExample))
                    sys.exit(1)
            else:
                puts(colored.red(noPathGiven))
                puts(colored.yellow(commandExample))
                sys.exit(1)
        else:
            puts(colored.red("Please enter path to the executable!"))
            puts(colored.yellow(commandExample))
            sys.exit(1)

        # Check if third argument(specific test case numbers) exists
        if self.args[2] and ((len(self.args) >= 4) or not self.options):
            try:
                toParse = str(self.args[2])
                # Remove last char if not int
                toParse = self.chechLastChar(toParse)

                # Different types of range

                # First type, e.g. 1-5 (both inclusive)
                if "-" in toParse:
                    splited = toParse.split("-")
                    if len(splited) == 2:
                        # Check if values for range are valid
                        self.checkRange(splited)
                        # Set which test cases to test
                        self.setTestCases(splited)
                    else:
                        self.invalidTestCaseRange()

                # Second type, e.g. 2..4 (both inclusive)
                elif ".." in toParse:
                    splited = toParse.split("..")
                    if len(splited) == 2:
                        # Check if values for range are valid
                        self.checkRange(splited)
                        self.setTestCases(splited)
                    else:
                        self.invalidTestCaseRange()

                # Third type, e.g. 4,5,7,10
                elif "," in toParse:
                    splited = toParse.split(",")
                    # Check if arguments are valid
                    for i in splited:
                        self.isInt(i)
                    # If all numbers are ok create test case list
                    self.testCases = map(int, splited)

                # Only one test case
                elif self.isInt(self.args[2]):
                    self.testCases.append(int(self.args[2]))

                # None of the types given, error
                else:
                    self.invalidTestCaseRange()

            except ValueError:
                puts(colored.red("Not a valid string for test case numbers!"))
                sys.exit(1)

    def modifyLog(self, stringBool, boolValue):
        if os.path.exists(self.tokenPath) and os.path.isfile(self.tokenPath):
            tokenFile = open(self.tokenPath, 'r')
        else:
            tokenFile = open(self.tokenPath, 'w+')
        list = []
        list.append(tokenFile.readline().rstrip())
        list.append(tokenFile.readline().rstrip())
        list[1] = stringBool
        tokenFile.close()
        tokenFile = open(self.tokenPath, 'w')
        tokenFile.writelines(list)
        tokenFile.close()
        self.showInfo = boolValue

    def chechLastChar(self, toParse):
        try:
            int(toParse[-1])
        except ValueError:
            toParse = toParse[:-1]
        return toParse

    def isInt(self, i):
        try:
            int(i)
            return True
        except ValueError:
            self.invalidTestCaseRange()

    def invalidTestCaseRange(self):
        puts(colored.red("Invalid Test Case number format!"))
        sys.exit(1)

    def checkRange(self, split):
        try:
            int(split[0])
            int(split[1])
        except ValueError:
            puts(colored.red("Parameter sequence or format is wrong!"))
            sys.exit(1)

    def setTestCases(self, split):
        self.testCases = range(int(split[0]), int(split[1]) + 1)

    def getFullPath(self, path):
        # fix given path
        if path[0] == "/" or path[0] == "\\":
            path = path[1:]
        # check if path is relative or absolute and return the full path
        if os.path.isabs(path):
            return path
        else:
            return os.path.abspath(path)


    def modifyEncoding(self, data):
        data['name'] = data['name'].encode('utf8')
        data['email'] = data['email'].encode('utf8')

    # Get the extension of the users file (executable)
    def getFileType(self, pathToFile):
        fileName = ''
        if "/" in pathToFile:
            fileName = pathToFile.split("/")[-1]
        elif "\\" in pathToFile:
            fileName = pathToFile.split("\\")[-1]
        type = fileName.split(".")[-1]
        self.fileType = type

    # No arguments given
    def checkIfNoArguments(self):
        if len(self.args) == 0:
            puts(colored.red("No arguments given! Use \"cae help\" for instructions."))
            sys.exit(1)


cli = CLI()
