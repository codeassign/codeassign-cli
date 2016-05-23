# codeassign-cli
Command line interface for CodeAssign

###Overview

This document describes the usage of the CodeAssign CLI interface.

The CLI is used for testing some or all test cases of a given problem.

All data is sent and recieved as JSON.

###Command

The keyword used is **"cae"** as in **"CodeAssign evaluate":**

**cae {problemId}  {pathToExecutable}  {testCaseIds}(optional)  {additionalOptions}(optional)** <br /> <br />

#####Examples:

- "cae  476  main/main.exe" 
- "cae  476  main/main.exe  1,2,4" 
- "cae  476  main/main.exe  5-7  -less"
- "cae  476  main/main.exe  4..6  -more" 

###Parameters

#####[REQUIRED] <br />



######{problemId}
The **first** parameter is the **"problemId"**, this is the id od the problem you want to test. This id can be found next to the problem name.
<br /> <br />

######{pathToExecutable}
The **second** parameter is the **path to your program executable**. The path can be **relative or apsolute**, with backslash or forslash. 
<br /><br />
Examples of correctly formated paths:

* **"/main/main.exe"**

* **"MyProgram\bin\main.exe"**

* **"C:/User/user/Desktop/main.exe"**
<br /> <br />


#####[OPTIONAL]


######{testCaseIds}

With this paremeter you can specify **which test cases** you want to run. If **left blank, all test cases** will be run.
<br />
####Examples:

- "1,2,3"
- "4-7"
- "3..6"
<br /> <br />

######{additionalOptions}

Last but not least, enter any **extra options** you might find useful:

####Available options:

######"-less"

Will display **only the most important information** on the screen. **This info is saved in ".codeassign" for later uses**. If you want to revert this use "-more".


######"-more" (default)

Will display **everything** (including user info) to the screen. **This info is saved in ".codeassign" for later uses**. If you want to revert this use "-less".



###Token

For first time usage you will be prompted to enter the **token associated to your account**. The token can be made on your profile on the official webpage : "www.codeassign.com"

If the token is valid, it will be **saved to your homedirectory(~/) in the ".codeassign" file**. Feel free to **modify the file if you want to change your token** number.


###Files

######"cae.exe"

The **main file** that does all the testing work.


######~/".codeassign"

This file is made after the first usage of CLI and consists of two (2) lines:

The **first line** has your **token** : "TOKEN="xxxxxxxx"

The **second line** saves info about your information **display option** (-less and -more).
