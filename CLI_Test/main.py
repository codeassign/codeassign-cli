# coding=utf-8
import os
import subprocess
import sys

import requests
from clint.arguments import Args
from clint.textui import puts, colored

import strings


class CLI():
    def __init__(self):

        # sys.path.insert(0, os.path.abspath('..'))

        # Used if user wants to test specific test cases (not all)
        self.testCases = []
        # GET problem path
        self.pathGetProblem = 'http://api.codeassign.com/Problem/'
        # GET TestCase values
        self.pathGetTestValues = 'http://api.codeassign.com/TestCase/'
        # POST evaluate TestCase (output)
        self.pathSetPostEvaluate = 'http://api.codeassign.com/Evaluate/'
        # POST AssociateConsoleToken
        self.pathAssociateToken = 'http://api.codeassign.com/AssociateConsoleToken/'

        # Problem id
        self.problemId = ''
        # Path to the user's exe file
        self.pathToExecutable = ''
        # File's extension
        self.fileType = ''
        # Token of user
        self.token = ''
        # internal list used to store the values from GET call
        self.values = []

        # List of outputs to evaluate
        self.outputList = []

        # Get all arguments from command line
        self.args = Args()
        self.checkIfNoArguments()

        # Check given arguments
        self.checkArguments()

        # Get test cases for given problem id
        self.values = self.getInputValues()

        # Check token
        self.tokenExists()
        # Evaluate each test
        self.evaluate()

    # Check if token is already created. If no token found prompt user for input
    def tokenExists(self):
        tokenPath = os.path.join(os.path.expanduser("~"), ".codeassign")

        # Token already exists
        if os.path.exists(tokenPath):
            if os.path.isfile(tokenPath):
                tokenFile = open(tokenPath, 'r')
                line = tokenFile.readline()
                # Check if file is properly formatted
                if len(line.split("=")) != 2:
                    puts(colored.red("Invalid token format in " + tokenPath))
                    sys.exit(1)
                token = line.split("=")[1]
                self.checkToken(token)
                # Not sure if needed for pretty output
                # puts(colored.yellow("Found existing token in: \"" + tokenPath + "\""))
                self.token = "?token=" + token
                tokenFile.close()
        # Create new token in ~/.codeassign
        else:
            puts(colored.yellow('No token file detected. Please enter your token: '))
            tokenInput = raw_input()
            self.checkToken(tokenInput)
            self.token = "?token=" + tokenInput
            tokenFile = open(tokenPath, 'w')
            stringToWrite = "APP_TOKEN=" + tokenInput
            tokenFile.write(stringToWrite)
            puts(colored.green("Token saved to: \"" + tokenPath + "\"\n"))
            tokenFile.close()

    def evaluate(self, ):

        # Test the code with input
        # os.system("Test.jar")
        for input in self.values:
            testCaseId = input['id']

            try:
                process = 0
                if self.fileType == "exe":
                    process = subprocess.Popen(self.pathToExecutable, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE).communicate(input['input'])
                elif self.fileType == "jar":
                    process = subprocess.Popen(['java', '-jar', self.pathToExecutable], stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE).communicate(input['input'])
                else:
                    puts(colored.red("Given type executable is not supported!"))
                    puts(colored.yellow("Currently supported file extensions: \".exe\", \".jar\""))
                    sys.exit(1)

                output = process[0]
                data = self.formatOutput(output, testCaseId)
                self.outputList.append(data)
            except OSError:
                puts(colored.red("ERROR! : Given file is not an executable!"))
                sys.exit(1)

        output = self.POSTEvaluate()

        # Check if something is wrong
        self.checkJsonStatusCode(output)

        # Check if tests passed evaluation
        passed = 0
        # Used for checking how many tests were really tested (user put too many)
        numberOfTests = 0
        if len(self.testCases) == 0:
            # Testing all available test cases
            for testCase in output['testCases']:
                numberOfTests += 1
                if self.checkTestCase(testCase):
                    passed += 1
            puts()
        # Testing specific test cases
        else:
            for testCase in output['testCases']:
                if testCase['id'] in self.testCases:
                    numberOfTests += 1
                    if self.checkTestCase(testCase):
                        passed += 1
            puts()

        self.printFinalResult(output, passed, numberOfTests)

    def POSTEvaluate(self):
        response = requests.post(self.pathSetPostEvaluate + str(self.problemId) + str(self.token), json=self.outputList)
        output = response.json()
        return output

    def formatOutput(self, output, testCaseId):
        data = {}
        data['id'] = testCaseId
        data['output'] = output
        return data

    def printFinalResult(self, output, passed, numberOfTests):
        if numberOfTests == 0 and len(self.testCases) > 0:
            puts(colored.red("Given test cases " + str(self.testCases) + " don't exist for problem with id " + str(
                self.problemId) + "!"))
            sys.exit(1)
        elif numberOfTests == 0:
            puts(colored.red("No test cases found for problem with id " + str(self.problemId) + "!"))
            sys.exit(1)
        # All tests passed
        if passed >= numberOfTests:
            puts(colored.green("\nAll (" + str(numberOfTests) + ") test/s passed! Well done!"))
        # All tests failed
        elif passed <= 0:
            puts(colored.red("All (" + str(numberOfTests) + ") test/s failed! Try again!"))
        # Some test failed
        else:
            puts("\nNumber of tests passed: " + str(passed) + "/" + str(len(output['testCases'])))
            puts(colored.yellow("Some tests failed! Almost there, keep trying!"))

    def checkJsonStatusCode(self, output):
        if "statusCode" in output.keys():
            if output['statusCode'] == requests.codes.unauthorized:
                puts(colored.red("Invalid token!"))
                sys.exit(1)
            elif output['statusCode'] != requests.codes.ok:
                puts(colored.red("Bad request!"))
                sys.exit(1)

    def checkTestCase(self, testCase):
        passed = 0
        if testCase['accepted']:
            puts('Test case number ' + str(testCase['id']) + ": " + colored.green("Passed!"))
            return True
        else:
            puts('Test case number ' + str(testCase['id']) + ": " + colored.red("Failed!"))
            return False

    # Get test cases for the given problemId
    def getInputValues(self):
        try:
            response = requests.get(self.pathGetTestValues + str(self.problemId))
            # Wrong problem id
            if not response.status_code == requests.codes.ok:
                puts(colored.red(strings.invalidProblemId))
                sys.exit(1)
            else:
                puts(colored.green(strings.problemIdOk))
            response.encoding = "utf8"
            data = response.json()
            return data

        except requests.ConnectionError:
            puts(colored.red(strings.connectionError))
            sys.exit(1)

    def checkArguments(self):
        # Check if first argument(problemId) is a valid number
        try:
            self.problemId = int(self.args[0])
        except ValueError:
            #  Help command entered
            if self.args[0] == "help":
                puts(colored.yellow(strings.commandExample))
            # Invalid input
            else:
                puts(colored.red(strings.firstArgumentInvalid))
            sys.exit(1)

        # Check if second argument(executable) is a valid file
        pathToFile = self.getFullPath(self.args[1])
        self.getFileType(pathToFile)
        if pathToFile:
            if os.path.exists(pathToFile):
                if os.path.isfile(pathToFile) and os.access(pathToFile, os.X_OK):
                    puts(colored.green(strings.fileValid))
                    self.pathToExecutable = pathToFile
                else:
                    puts(colored.red(strings.notAFile))
                    puts(colored.yellow(strings.commandExample))
                    sys.exit(1)
            else:
                puts(colored.red(strings.noPathExists))
                puts(colored.yellow(strings.commandExample))
                sys.exit(1)
        else:
            puts(colored.red(strings.noPathGiven))
            puts(colored.yellow(strings.commandExample))
            sys.exit(1)

        # Check if third argument(specific test case numbers) exists
        if self.args[2]:
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
            puts("Incorrect range for Test Cases given!")
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

    def checkToken(self, tokenInput):
        response = requests.post(self.pathAssociateToken + tokenInput)
        # Check if status not 200
        if response.status_code != requests.codes.ok:
            puts(colored.red("Bad request!2"))
            sys.exit(1)

        data = response.json()

        # Modify encoding of account info
        self.modifyEncoding(data)

        # Check if wrong token
        if 'errorMessage' in data.keys():
            puts(colored.red("Invalid token!"))
            sys.exit(1)

        # Token is ok
        if data['success']:
            puts(colored.green("Token is valid!\n"))
            formatNum = len(data['email']) + 8
            puts(" " * (formatNum / 3) + colored.yellow("Account info"))
            nameLen = len(data['name']) + 8
            puts("|" + "=" * formatNum + "|")
            # puts(colored.yellow("\tAccount info"))

            puts("| " + colored.yellow("Name: ") + " " + data['name'] + " " * (
                formatNum - nameLen) + "|\n| " + colored.yellow(
                "Email: ") + data['email'] + "|")
            puts("|" + "=" * formatNum + "|")
            puts()
            return True

    def modifyEncoding(self, data):
        data['name'] = data['name'].encode('cp1250')
        data['email'] = data['email'].encode('cp1250')

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
