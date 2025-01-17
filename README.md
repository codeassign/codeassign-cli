# codeassign-cli
Command line interface for CodeAssign

## Overview

This document describes the installation and usage of the CodeAssign CLI.

The CLI is used for testing some or all test cases of a given problem.

After you installed `cae` on your computer be sure to checkout our [Hello World! Guide](http://codeassign.com/guide). And if you are having trouble with running your solution of [Hello World!](http://codeassign.com/groups/39/problems/87) problem, be sure to checkout [our solutions](https://github.com/codeassign/codeassign-cli/tree/master/hello_world) in **6** different languages: **Python2**, **Python3**, **C**, **C++**, **Ruby**, **Bash** and **Java**.

## Installation

CodeAssign CLI works on Windows and Linux. We created stand-alone executables for these platforms so you don't have to worry about any dependantcies. Please, follow instructions for your platform. If your platform isn't listed or stand-alone executable version doesn't work on your computer, checkout universal instructions.

### Windows

Just download `cae.exe` [here](https://github.com/codeassign/codeassign-cli/raw/master/windows/cae.exe). You can find this file in [`windows`](https://github.com/codeassign/codeassign-cli/tree/master/windows) folder of this project.

Your `cae.exe` is now probably saved in your `C:\Users\<YOUR USERNAME>\Downloads` folder. If you now open `cmd.exe` in this folder, you will be able to run `cae` command. And if you do this you will get this message: `No arguments given! Use "cae help" for instructions.`, and that's **OK**!

You are now ready to test your [Hello World!](http://codeassign.com/groups/39/problems/87) solution. Be sure to check our [Hello World! Guide](http://codeassign.com/guide) if you have any trouble solving and evaluating this example.

##### Global installation

The above guide explains simplest and minimum steps that you have to do before running `cae` command. But now your `CMD` only knows about `cae` command if you position yourself in the folder where `cae` is located, i.e. probably your `C:\Users\<YOUR USERNAME>\Downloads`. If you want your `CMD` to know about your `cae` command in the **whole system** (i.e. you will be able to run `cae` anywhere in your `CMD`), this is what you need to do:

1. Copy `cae.exe` somewhere safe. We suggest you to create a `CodeAssign` folder in your `C:\` drive and place `cae.exe` there. So now `cae.exe` will be located in `C:\CodeAssign\cae.exe`.

2. Open your *Control Panel* and go to *System and Security* > *System*.

3. On the left you will see *Advanced system settings*. Click on that and new window should open.

4. Now click on *Advanced* tab, and there at the bottom of the window you should see *Environment Variables...* button. Click on that button and new window should open.

5. In this window you should see two sections: `User variables for <YOUR USERNAME>` and `System variables`. In this second section find and select variable called `Path`.

6. With the variable `Path` selected click *Edit...* button (new window should open).

7. Depending on Windows version you have you will see either: nice table with some paths, or old and dirty text filed with paths separated with `;`:

    * If you see a table, click on the *New* button and enter `C:\CodeAssign\`.
    * If you see old and dirty text field enter: `;C:\CodeAssign\`. **DON'T FORGET `;` BEFORE YOUR PATH**.

8. Click *OK* as many times as you can to exit from all windows.

9. Restart your PC.

10. Open your `CMD` and type `cae`. You should again see this message: `No arguments given! Use "cae help" for instructions.`, and that's **OK**!

11. You are now ready to test your [Hello World!](http://codeassign.com/groups/39/problems/87) solution. Be sure to check our [Hello World! Guide](http://codeassign.com/guide) if you have any trouble solving and evaluating this example.

### Linux

1. [Download](https://github.com/codeassign/codeassign-cli/archive/master.zip) or clone this project.

2. Copy `linux/cae` in `/usr/local/bin` folder

  ```
  $ sudo cp linux/cae /usr/local/bin
  ```

3. Make sure `cae` is executable

  ```
  $ sudo chmod +x /usr/local/bin/cae
  ```

4. You are now ready to test your [Hello World!](http://codeassign.com/groups/39/problems/87) solution. Be sure to check our [Hello World! Guide](http://codeassign.com/guide) if you have any trouble solving and evaluating this example.


### Universal

If your platform isn't listed above or the precompiled version we provide doesn't work on your computer, please follow these instructions.

1. Install [python2.7](https://www.python.org/downloads/).

2. Install [pip](https://pypi.python.org/pypi/pip).

3. Using `pip` install dependantcies:

  ```
  $ pip install requests
  $ pip install clint
  ```
4. You should now be able to run `cae.py`.

5. You are now ready to test your [Hello World!](http://codeassign.com/groups/39/problems/87) solution. Be sure to check our [Hello World! Guide](http://codeassign.com/guide) if you have any trouble solving and evaluating this example.

#### Optional

After completing **Universal** steps above you can create stand-alone executable for your system. First install `pyinstaller` using `pip`:

```
$ pip install pyinstaller
```

Then for Linux or OSX run `build_linux.sh` script and for Windows run `build_windows.bat` script.

Your executable will be present in `linux` or `windows` folder.

## Command

The keyword used is `cae` (**C**ode**A**ssign **e**valuate):

```
cae {problemId} {pathToExecutable} {testCaseIds}(optional)  {additionalOptions}(optional)
```

#### Examples:

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
