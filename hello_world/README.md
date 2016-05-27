# Hello World

This file provides detailed instructions on how to use `cae` with different languages. Before reading this file please install `cae` and read our [basic guide](http://codeassign.com/guide).

## Intro

The only thing you need to remember when using `cae` is the following: **It only runs executable files**. So it doesn't care about language you used for solving your solution. It just cares it can run the file you gave it.

So the first step before running `cae` is:

1. Make sure your solution is executable

This means you can run your solution like this:

  * Linux: `./mysolution` (or with any other extension)
  * Windows: `mysolution` (or with any other extension)

On Windows you can create runnable scripts by creating `.bat` file and writing your commands there:

```
@ECHO OFF
java MySolution
```

## Python

Checkout solutions in [Python2](https://github.com/codeassign/codeassign-cli/blob/clean/hello_world/hello_world.2.py) and [Python3](https://github.com/codeassign/codeassign-cli/blob/clean/hello_world/hello_world.3.py).

Running these is simple as:

```
$ cae 87 hello_world.2.py
$ cae 87 hello_world.3.py
```

If you are on Windows and you can't run `hello_world.2.py` with `hello_world.2.py` command when you should create a `.bat` script that will do this for you:

1. Create `hello_world.bat` file.
2. Write this inside it:

  ```
  @ECHO OFF
  python hello_world.2.py
  ```
3. Run `cae`:

  ```
  $ cae 87 hello_world.bat
  ```

## C

1. Compile your solution:

  ```
  $ gcc hello_world.c -o hello_world.o
  ```

2. Run `cae`:

  ```
  $ cae 87 hello_world.o
  ```

## C++

1. Compile your solution:

  ```
  $ g++ hello_world.cpp -o hello_world.o
  ```

2. Run `cae`:

  ```
  $ cae 87 hello_world.o
  ```

## Ruby

See **Python** but insted of `python` command you use `ruby` command and `hello_world.rb` file.

## Bash

1. Run `cae`:

  ```
  $ cae 87 hello_world.sh
  ```

## Java

Java projects can be run if they are packaged into a single executable JAR which you can run with `java -jar *yourjar.jar*`.

Assuming your classes are in a single folder and the main class is called HelloWorld, you can build this by running

```
javac *.java;
jar cfe MySolution.jar HelloWorld *.class;
```

If `java -jar MySolution.jar` now properly works, add the executable permission to the jar and test it with `cae`.

```
chmod +x MySolution.jar;
cae 87 MySolution.jar;
```

You can package the whole process into a simple compile-build-test script:

```
javac *.java;
jar cfe MySolution.jar HelloWorld *.class;
chmod +x MySolution.jar;
cae 87 MySolution.jar;
```
