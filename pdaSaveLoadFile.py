import os
import csv
from pdaConstants import *

SEPARATOR = ','
RELATIVE_DIRECTORY = "log/"

FILENAME_BASE = "log"
FILENAME_BASE_EXTENSION = ".csv"
FILENAME_EXTRA_EXTENSION = ".txt"
FILENAME_EXTRA_SUFFIX = "extra"
fileId = 0

# Gets the absolute path to the directory absolute path, relative to the program (https://stackoverflow.com/a/25612797)
script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
pathToDirectory = os.path.join(script_dir, RELATIVE_DIRECTORY)

# Create the directory if doesn't exist
if not os.path.exists(os.path.dirname(pathToDirectory)):
        os.makedirs(os.path.dirname(pathToDirectory))
        os.chmod(pathToDirectory, 0o777) # Give the permission to all users change the directory contents. 0o stands for octal.
        # This permission handling was needed, if the code was runned by su

# Increases by 1 the id of the filename, if it already exists
while os.path.exists(os.path.join(pathToDirectory, FILENAME_BASE + str(fileId) + ".csv")):
    fileId += 1

# The final filename
fullPathFilename = os.path.join(pathToDirectory, FILENAME_BASE + str(fileId)) + FILENAME_BASE_EXTENSION
fullPathFilenameExtra = os.path.join(pathToDirectory, FILENAME_BASE + str(fileId)) + FILENAME_EXTRA_SUFFIX + FILENAME_EXTRA_EXTENSION

# Writes the header to the CSV
fileVariable = open(fullPathFilename, "a")
csv.writer(fileVariable, delimiter=SEPARATOR).writerow(DATA_LIST_CSV_HEADER_NAME)
fileSizeWithJustHeader = os.stat(fullPathFilename).st_size
fileVariable.close()

def writeStringToExtraFile(stringToWrite):
    fileVariable = open(fullPathFilenameExtra, "a")
    fileVariable.write(stringToWrite)
    fileVariable.close()

def appendListToFile(listToAppend):
    # Opens the file with append
    fileVariable = open(fullPathFilename, "a")
    csv.writer(fileVariable, delimiter=SEPARATOR).writerow(listToAppend)
    fileVariable.close()

# Unused
def deleteFileIfEmpty():
    if (os.stat(fullPathFilename).st_size == fileSizeWithJustHeader): # If the file is empty
        os.remove(fullPathFilename)
    os.chmod(fullPathFilename, 0o666) # Gives the file all permissions, except executing.
