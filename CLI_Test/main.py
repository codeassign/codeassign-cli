import filecmp
import os
import subprocess

import requests
from clint.arguments import Args
from clint.textui import puts, colored, indent

import strings


class CLI():
    def __init__(self):

        # sys.path.insert(0, os.path.abspath('..'))

        # list of id's of test cases, used to determine which test cases to test (if the user wants to run specific tests not all)
        self.testCases = []
        # get problem path
        self.pathGetProblem = 'http://api.codeassign.com/Problem'
        # get TestCase values
        self.pathGetTestValues = 'http://api.codeassign.com/TestCase/'

        # internal list used to store the values from GET call
        self.values = []

        self.args = Args()
        with indent(4, quote='>>>'):
            puts(colored.red('Aruments passed in: ') + str(self.args.all))
            puts(colored.red('Flags detected: ') + str(self.args.flags))
            puts(colored.red('Files detected: ') + str(self.args.files))
            puts(colored.red('NOT Files detected: ') + str(self.args.not_files))
            puts(colored.red('Grouped Arguments: ') + str(dict(self.args.grouped)))

        self.checkArguments()
        self.values = self.getInputValues()
        self.evaluate()

    def evaluate(self, ):
        # test the code with input
        # os.system("Test.jar")
        # p = subprocess.Popen(['java', '-jar', 'Test.jar'])
        for input in self.values:
            print input['input']
            process = subprocess.Popen('test.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE)._communicate(
                input['input'])
            output = process[0]
            print output

            # TODO send output to validate on server

    # Check if the Id is a valid problem id (the problem with this id exists)
    # If it exists, get it, else exit and print error
    def getInputValues(self):

        try:
            # response = requests.get(self.pathGetProblem + str(self.args[0]))
            response = requests.get(self.pathGetTestValues + str(self.problemId))
            print response.status_code
            if not response.status_code == requests.codes.ok:
                puts(colored.red(strings.invalidProblemId))
                exit(1)
            else:
                puts(colored.green(strings.problemIdOk))
            # data = response.json()
            response.encoding = strings.encoding
            data = response.json()
            return data
        except requests.ConnectionError:
            print strings.connectionError

    def checkArguments(self):
        # Check if first argument is a valid number
        try:
            self.problemId = int(self.args[0])
        except ValueError:
            print strings.firstArgument

        # Check if second argument is a valid file
        if self.args[1]:
            if os.path.exists(self.args[1]):
                if os.path.isfile(self.args[1]):
                    puts(colored.green(strings.fileValid))
                else:
                    puts(colored.red(strings.notAFile))
                    puts(colored.yellow(strings.commandExample))
                    # exit(1)
            else:
                puts(colored.red(strings.noPathExists))
                puts(colored.yellow(strings.commandExample))
                # exit(1)
        else:
            puts(colored.red(strings.noPath))
            puts(colored.yellow(strings.commandExample))
            # exit(1)

        # Check if third argument exists
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
                    for i in splited:
                        self.isInt(i)
                    # If all numbers are ok create test case list
                    self.testCases = splited
                    print self.testCases

                # None of the types given, error
                else:
                    self.invalidTestCaseRange()

            except ValueError:
                print "Not a valid string!"

    def chechLastChar(self, toParse):
        try:
            int(toParse[-1])
        except ValueError:
            toParse = toParse[:-1]
        return toParse

    def isInt(self, i):
        try:
            int(i)
        except ValueError:
            self.invalidTestCaseRange()

    def invalidTestCaseRange(self):
        print "Invalid Test Case number format!"
        exit(1)

    def checkRange(self, split):
        try:
            int(split[0])
            int(split[1])
        except ValueError:
            print "Incorrect range for Test Cases given!"
            exit(1)

    def setTestCases(self, split):
        self.testCases = range(int(split[0]), int(split[1]) + 1)
        print self.testCases

    def compareFiles(self, first, second):
        if (filecmp.cmp(first, second)):
            return 1
        return 0

    def getProblemName(self, path):
        parts = path.split("/")
        print parts
        return parts[-1]

    def getFullPath(self, path):
        # fix given path
        if path[0] == "/" or path[0] == "\\":
            path = path[1:]
        # check if path is relative or absolute and return the full path
        if os.path.isabs(path):
            return path
        else:
            return os.path.abspath(path)


cli = CLI()
