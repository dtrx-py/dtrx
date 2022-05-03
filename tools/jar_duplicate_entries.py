"""
hacky script to insert duplicate entries to a .jar file
"""

import zipfile

# First run these commands
# $ echo hello > hello.txt
# $ jar --create --file test.jar hello.txt

with zipfile.ZipFile("test.jar", "a") as zf:
    zf.write("hello.txt")
