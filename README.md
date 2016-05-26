# codeassign-cli
Command line interface for CodeAssign

## Overview

This document describes the usage of the CodeAssign CLI interface.

The CLI is used for testing some or all test cases of a given problem.

## Command

The keyword used is `cae` (**C**ode**A**ssign **e**valuate):

```
cae {problemId} {pathToExecutable} {testCaseIds}(optional)  {additionalOptions}(optional)
```

### Examples:

```
$ cae 476 main/main.exe
$ cae 476 main/main.exe 1,2,4
$ cae 476 main/main.exe 5-7 -less
$ cae 476 main/main.exe 4..6 -more
```

## Parameters

#### `{problemId}` - required

The **first** parameter is the `problemId`, this is the id od the problem you want to test. This id can be found next to the problem name.

#### `{pathToExecutable}` - required

The **second** parameter is the **path to your program executable**. The path can be **relative or apsolute**.

Examples of correctly formated paths:

* `/main/main.exe`

* `MyProgram\bin\main.exe`

* `C:/User/user/Desktop/main.exe`

#### `{testCaseIds}` - optional

With this paremeter you can specify **which test cases** you want to run. If **left blank, all test cases** will be run.

##### Examples:

* `1,2,3`
* `4-7`
* `3..6`

#### `{additionalOptions}` - optional

Last but not least, enter any **extra options** you might find useful:

##### Available options:

###### `-less`

Will display **only the most important information** on the screen. **This info is saved in `~/.codeassign` for later uses**. If you want to revert this use `-more`.


###### `-more` - default

Will display **everything** (including user info) to the screen. **This info is saved in `~/.codeassign` for later uses**. If you want to revert this use `-less`.


## Token

For first time usage you will be prompted to enter the **token associated to your account**. The tokens for your account can be generated [here](http://codeassign.com/tokens) (login required). Tokens are just used to identify who you are on [CodeAssign](http://codeassign.com).

If the token is valid, it will be **saved in `~/.codeassign` file**. Feel free to modify the file if you want to change your token number.


## Files

### `cae.exe`

The **main file** that does all the testing work.


### `~/.codeassign`

This file is made after the first usage of CLI and consists of two (2) lines:

The **first line** has your **token** : `TOKEN="xxxxxxxx`

The **second line** saves info about your information **display option** (`-less` and `-more`).
