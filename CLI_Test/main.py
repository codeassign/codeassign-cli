import filecmp
import sys
import os
from clint.arguments import Args
from clint.textui import puts, colored, indent


def compareFiles(first, second):
    if (filecmp.cmp(first, second)):
        return 1
    return 0


def getProblemName(path):
    parts = path.split("/")
    print parts
    return parts[-1]


def getFullPath(path):
    # fix given path
    if path[0] == "/" or path[0] == "\\":
        path = path[1:]
    # check if path is relatie or absolute and return the full path
    if os.path.isabs(path):
        return path
    else:
        return os.path.abspath(path)

sys.path.insert(0, os.path.abspath('..'))

args = Args()

with indent(4, quote='>>>'):
    puts(colored.red('Aruments passed in: ') + str(args.all))
    puts(colored.red('Flags detected: ') + str(args.flags))
    puts(colored.red('Files detected: ') + str(args.files))
    puts(colored.red('NOT Files detected: ') + str(args.not_files))
    puts(colored.red('Grouped Arguments: ') + str(dict(args.grouped)))

print getProblemName("http://www.mysite.com")

print getFullPath("Desktop\lab1")
print
