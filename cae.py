#!/usr/bin/env python2
# coding=utf-8
import os
import subprocess
import sys

import platform

import requests
import csv
from clint.arguments import Args
from clint.textui import puts, colored

encodingISO = 'ISO-8859-1'
encodingUTF8 = 'utf_8'


class CLI:

    class Strings:
        INPUT_EXECUTABLE_PATH = "Please enter path to the executable!"
        NOT_EXECUTABLE = "ERROR! : Given file is not an executable! (Did you add the path of your compiler to PATH?)"
        INVALID_TOKEN = "Invalid token!"
        BAD_REQUEST = "Bad request!"
        NO_ARGUMENTS_GIVEN = "No arguments given! Use \"cae help\" for instructions."
        NO_TOKEN_FOUND = "In order to know we're going to need your token. You can get one at https://codeassign.com/tokens"
        NO_PATH_GIVEN = "No path given. Please enter path to the testing file!"
        PATH_DOES_NOT_EXIST = "Given path does not exist!"
        INPUT_TOKEN = "Please input your token: "
        NOT_A_FILE = "Given path is not a file or an executable!"
        FILE_IS_VALID = "File is valid!"
        INVALID_PROBLEM_ID = "Invalid problem Id! (Error 404)"
        FIRST_ARGUMENT_INVALID = "First argument must be the problem id!"
        CONNECTION_ERROR = "Connection error!"
        COMMAND_EXAMPLE = "Command example: \"cae 576 /test/main.exe 1,2,3\"\nLast argument is optional and can be in formats: \"1,2,3\" \"3-7\" \"2..5\", tests all if left blank."
        PROBLEM_ID_OK = "Problem id OK!"

    class Endpoints(object):
        POST_EVALUATE = "https://api.codeassign.com/Evaluate/"
        POST_ASSOCIATE_TOKEN = "https://api.codeassign.com/AssociateConsoleToken/"
        GET_TEST_CASES = "https://api.codeassign.com/TestCase/"

        @staticmethod
        def get_test_case_endpoint(problem_id):
            return CLI.Endpoints.GET_TEST_CASES + str(problem_id)

        @staticmethod
        def get_evaluation_endpoint(problem_id, token):
            return CLI.Endpoints.POST_EVALUATE + str(problem_id) + "?token=" + token

        @staticmethod
        def get_associate_token_endpoint(token):
            return CLI.Endpoints.POST_ASSOCIATE_TOKEN + token

    class Properties:
        KEY_TOKEN = "APP_TOKEN"
        KEY_LOG = "LOG"

        DEFAULT_PROPERTIES_FILE = ".codeassign"

        propertiesFilePath = os.path.join(os.path.expanduser("~"), DEFAULT_PROPERTIES_FILE)
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

        # List of ints, used if user wants to test specific test cases (not all)
        self.testCases = []

        # Path to log file
        self.logFilePath = os.path.join(os.getcwd(), "cae_log.txt")

        # Problem id
        self.problemId = ''
        # Path to the user's exe file
        self.pathToExecutable = ''
        # File's extension
        self.fileType = ''
        # Which compiler should be used
        self.compilerType = ''

        # Check if user wants more or less info
        self.showInfo = True
        # Additional options used in argument
        self.options = False
        # Wrote to log file
        self.logFileBool = False
        # First time log
        self.firstLog = True

        properties = CLI.Properties()

        args = Args()
        self.exit_if_no_arguments(args)
        self.load_arguments(args, properties)

        # Get test cases for given problem id
        inputs = self.get_inputs(self.problemId)

        token = self.load_token(properties)

        # Evaluate each test
        self.evaluate(inputs, self.problemId, token)

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

    @staticmethod
    def request_token():
        sys.stdout.write(CLI.Strings.INPUT_TOKEN)
        return raw_input().rstrip()

    def validate_token(self, token):
        response = requests.post(CLI.Endpoints.get_associate_token_endpoint(token))
        # Check if status not 200
        if response.status_code != requests.codes.ok:
            puts(colored.red(CLI.Strings.BAD_REQUEST))
            return False

        data = response.json()
        # Check if wrong token
        if 'errorMessage' in data.keys():
            puts(colored.red(CLI.Strings.INVALID_TOKEN))
            return False

        # Modify encoding of account info
        self.modify_encoding(data)

        # Token is ok
        if data['success'] and self.showInfo:
            puts(colored.green("Token is valid!\n"))
            format_num = len(data['email'].decode('utf8')) + 8
            puts(" " * (format_num / 3) + colored.yellow("Account info"))
            name_length = len(data['name'].decode('utf8')) + 8
            puts("|" + "=" * format_num + "|")

            puts("| " + colored.yellow("Name: ") + " " + data['name'] + " " * (
                format_num - name_length) + "|\n| " + colored.yellow(
                "Email: ") + data['email'] + "|")
            puts("|" + "=" * format_num + "|")
            puts()
            return True

    # Test the code with input
    def evaluate(self, inputs, problem_id, token):
        output_list = []

        for test_case in inputs:
            test_case_id = test_case['id']
            # Check which compiler to use based on the self.fileType
            self.set_compiler_type()
            try:
                process = subprocess.Popen(self.compilerType, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, shell=False).communicate(test_case['input'])
                output = process[0]
                data = self.format_output(output, test_case_id)
                output_list.append(data)
            except OSError:
                puts(colored.red(CLI.Strings.NOT_EXECUTABLE))
                sys.exit(1)

        output = self.validate_on_server(problem_id, output_list, token)
        # Check if something is wrong
        self.check_json_status_code(output)
        # Used to check if tests passed evaluation
        passed = 0
        # Used for checking how many tests were really tested (if user put too many)
        number_of_tests = 0

        # Dictionary of test cases
        test_case_dict = {}
        # Count used only for output log formatting
        count = 1
        # Another count ( yeah ) , for the right output number when there are only specific test cases, used for log
        count_specific_file = 1
        # Dictionary keys
        i = 1
        
        # Write output log
        for testCase in output['testCases']:
            # Add new dictionary value, e.g. "1 : True"
            test_case_dict[i] = testCase['accepted']
            i += 1
            # Check if the output for this test case should be visible
            if not testCase['hiddenOutput']:
                # Write test status to log file if LOG=True(-more is given as a parameter)
                # If there are specific test cases
                if len(self.testCases) > 0:
                    if self.showInfo and (count_specific_file in self.testCases):
                        self.write_log(count_specific_file, testCase)
                    count_specific_file += 1
                else: # Write all test cases
                    if self.showInfo:
                        self.write_log(count, testCase)
                        count += 1

        # Something was written to file
        if count > 1 or count_specific_file > 0:
            self.logFileBool = True

        # Count specific, same as the above count, this one is used for command line output
        count_specific_output = 1

        # Check if there are specific test cases given by user
        if len(self.testCases) == 0:
            # Testing all available test cases
            for key in sorted(test_case_dict):
                number_of_tests += 1
                if self.check_test_case(number_of_tests, test_case_dict[key]):
                    passed += 1
            puts()
        # Testing only specific test cases
        else:	
            for key in sorted(test_case_dict):
                if key in self.testCases:
                    number_of_tests += 1
                    if self.check_test_case(count_specific_output, test_case_dict[key]):
                        passed += 1
                count_specific_output += 1
            puts()

        self.print_final_result(problem_id, output, passed, number_of_tests)

    def set_compiler_type(self):
        if self.fileType == 'jar':
            self.compilerType = ['java', '-jar', self.pathToExecutable]
            return
        
        f = open(self.pathToExecutable, 'r')
        first_line = f.readline()
        f.close()

        if platform.system() == 'Windows' or first_line[:2] != '#!':
            if self.fileType == "py":
                self.compilerType = ['python', self.pathToExecutable]
            elif self.fileType == "rb":
                self.compilerType = ['ruby', self.pathToExecutable]
            else:
                self.compilerType = [self.pathToExecutable]
        else:
            self.compilerType = [self.pathToExecutable]

    def write_log(self, count, test_case):
        # Used for formating
        separator = "=================================\n\n"

        # Format output for log file
        if test_case['accepted']:
            header = '>>>Test case number ' + str(count) + ": " + "Passed!<<<\nInput:\n"
        else:
            header = '>>>Test case number ' + str(count) + ": " + "Failed!<<<\n\nInput:\n"
        test_case_input = test_case['input'].rstrip() + "\n\n"
        # Separator
        user_output_text = "Your output:\n"
        user_output = test_case['userOutput'].rstrip() + "\n\n"
        req_output_text = "Required output:\n"
        req_output = test_case['requiredOutput'].rstrip() + "\n\n"
        # Separator
        
        if self.firstLog:
            log_file = open(self.logFilePath, 'w')
            self.firstLog = False
        else:
            log_file = open(self.logFilePath, 'a')
        # Combine the formatted output
        full_log = header + test_case_input + separator + user_output_text + user_output + req_output_text + req_output + separator + "\n"
        log_file.write(full_log)
        log_file.close()

    @staticmethod
    def validate_on_server(problem_id, output_list, token):
        return requests.post(CLI.Endpoints.get_evaluation_endpoint(problem_id, token), json=output_list).json()

    @staticmethod
    def format_output(output, test_case_id):
        return {'id': test_case_id, 'output': output}

    def print_final_result(self, problem_id, output, passed, number_of_tests):
        # Given test cases don't exist
        if number_of_tests == 0 and len(self.testCases) > 0:
            puts(colored.red("Given test cases " + str(self.testCases) + " don't exist for problem with id " + str(
                problem_id) + "!"))
            sys.exit(1)
        # No tests found
        elif number_of_tests == 0:
            puts(colored.red("No test cases found for problem with id " + str(problem_id) + "!"))
            sys.exit(1)

        # Log was created and LOG=True(-more is used)
        if self.logFileBool and self.showInfo:
            puts(colored.yellow("Check log file \"cae_log\" in your working directory for more detailed info!"))

        # All tests passed
        if passed >= number_of_tests:
            puts(colored.green("\nAll (" + str(number_of_tests) + ") test/s passed! Well done!"))
        # All tests failed
        elif passed <= 0:
            puts(colored.red("\nAll (" + str(number_of_tests) + ") test/s failed! Try again!"))
        # Some test failed
        else:
            puts("\nNumber of tests passed: " + str(passed) + "/" + str(len(output['testCases'])))
            puts(colored.yellow("Some tests failed! Almost there, keep trying!"))

    @staticmethod
    def check_json_status_code(output):
        if "statusCode" in output.keys():
            if output['statusCode'] == requests.codes.unauthorized:
                puts(colored.red("Invalid token!2"))
                sys.exit(1)
            elif output['statusCode'] != requests.codes.ok:
                puts(colored.red("Bad request!"))
                sys.exit(1)

    @staticmethod
    def check_test_case(key, value):
        if value:
            puts('Test case number ' + str(key) + ": " + colored.green("Passed!"))
            return True
        else:
            puts('Test case number ' + str(key) + ": " + colored.red("Failed!"))
            return False

    # Get test cases for the given problemId
    def get_inputs(self, problem_id):
        try:
            response = requests.get(CLI.Endpoints.get_test_case_endpoint(problem_id))
            # Wrong problem id
            if not response.status_code == requests.codes.ok:
                puts(colored.red(CLI.Strings.INVALID_PROBLEM_ID))
                sys.exit(1)
            else:
                # Show if user wants more info (LOG=True)
                if self.showInfo:
                    puts(colored.green(CLI.Strings.PROBLEM_ID_OK))
            response.encoding = "utf8"
            return response.json()

        except requests.ConnectionError:
            puts(colored.red(CLI.Strings.CONNECTION_ERROR))
            sys.exit(1)

    def load_arguments(self, args, properties):
        # Check for additional options and modify internal values accordingly
        if "-" in args[len(args) - 1]:
            if args[-1] == "-less":
                properties.set_log(False)
                properties.save()
                self.options = True
            if args[-1] == "-more":
                properties.set_log(True)
                properties.save()
                self.options = True
        else:
            self.showInfo = properties.get_log()

        # Check if first argument(problemId) is a valid number
        try:
            self.problemId = int(args[0])
        except ValueError:
            #  Help command entered
            if args[0] == "help":
                puts(colored.yellow(CLI.Strings.COMMAND_EXAMPLE))
            # Invalid input
            else:
                puts(colored.red(CLI.Strings.FIRST_ARGUMENT_INVALID))
            sys.exit(1)

        # Check if second argument(executable) is a valid file
        if args[1]:
            path_to_file = self.get_full_path(args[1])
            self.fileType = self.get_file_extension(path_to_file)
            if path_to_file:
                if os.path.exists(path_to_file):
                    if os.path.isfile(path_to_file) and os.access(path_to_file, os.X_OK):
                        # Show if user wants more info (LOG=True)
                        if self.showInfo:
                            puts(colored.green(CLI.Strings.FILE_IS_VALID))
                        self.pathToExecutable = path_to_file
                    else:
                        puts(colored.red(CLI.Strings.NOT_A_FILE))
                        puts(colored.yellow(CLI.Strings.COMMAND_EXAMPLE))
                        sys.exit(1)
                else:
                    puts(colored.red(CLI.Strings.PATH_DOES_NOT_EXIST))
                    puts(colored.yellow(CLI.Strings.COMMAND_EXAMPLE))
                    sys.exit(1)
            else:
                puts(colored.red(CLI.Strings.NO_PATH_GIVEN))
                puts(colored.yellow(CLI.Strings.COMMAND_EXAMPLE))
                sys.exit(1)
        else:
            puts(colored.red(CLI.Strings.INPUT_EXECUTABLE_PATH))
            puts(colored.yellow(CLI.Strings.COMMAND_EXAMPLE))
            sys.exit(1)

        # Check if third argument(specific test case numbers) exists
        if args[2] and ((len(args) >= 4) or not self.options):
            try:
                to_parse = str(args[2])
                # Remove last char if not int
                to_parse = self.trim_last_char_if_not_int(to_parse)

                # Different types of range

                # First type, e.g. 1-5 (both inclusive)
                if "-" in to_parse:
                    splited = to_parse.split("-")
                    if len(splited) == 2:
                        # Check if values for range are valid
                        self.check_range(splited)
                        # Set which test cases to test
                        self.set_test_cases(splited)
                    else:
                        self.invalid_test_case_range()

                # Second type, e.g. 2..4 (both inclusive)
                elif ".." in to_parse:
                    splited = to_parse.split("..")
                    if len(splited) == 2:
                        # Check if values for range are valid
                        self.check_range(splited)
                        self.set_test_cases(splited)
                    else:
                        self.invalid_test_case_range()

                # Third type, e.g. 4,5,7,10
                elif "," in to_parse:
                    splited = to_parse.split(",")
                    # Check if arguments are valid
                    for i in splited:
                        self.is_int(i)
                    # If all numbers are ok create test case list
                    self.testCases = map(int, splited)

                # Only one test case
                elif self.is_int(args[2]):
                    self.testCases.append(int(args[2]))

                # None of the types given, error
                else:
                    self.invalid_test_case_range()

            except ValueError:
                puts(colored.red("Not a valid string for test case numbers!"))
                sys.exit(1)

    @staticmethod
    def trim_last_char_if_not_int(to_parse):
        try:
            int(to_parse[-1])
        except ValueError:
            to_parse = to_parse[:-1]
        return to_parse

    def is_int(self, i):
        try:
            int(i)
            return True
        except ValueError:
            self.invalid_test_case_range()

    @staticmethod
    def invalid_test_case_range():
        puts(colored.red("Invalid Test Case number format!"))
        sys.exit(1)

    @staticmethod
    def check_range(split):
        try:
            int(split[0])
            int(split[1])
        except ValueError:
            puts(colored.red("Parameter sequence or format is wrong!"))
            sys.exit(1)

    def set_test_cases(self, split):
        self.testCases = range(int(split[0]), int(split[1]) + 1)

    @staticmethod
    def get_full_path(path):
        # fix given path
        if path[0] == "/" or path[0] == "\\":
            path = path[1:]
        # check if path is relative or absolute and return the full path
        if os.path.isabs(path):
            return path
        else:
            return os.path.abspath(path)

    @staticmethod
    def modify_encoding(data):
        data['name'] = data['name'].encode('utf8')
        data['email'] = data['email'].encode('utf8')

    # Get the extension of the users file (executable)
    @staticmethod
    def get_file_extension(path_to_file):
        file_name = ''
        if "/" in path_to_file:
            file_name = path_to_file.split("/")[-1]
        elif "\\" in path_to_file:
            file_name = path_to_file.split("\\")[-1]
        file_type = file_name.split(".")[-1]
        return file_type

    @staticmethod
    def exit_if_no_arguments(args):
        if len(args) == 0:
            puts(colored.red(CLI.Strings.NO_ARGUMENTS_GIVEN))
            sys.exit(1)


cli = CLI()
