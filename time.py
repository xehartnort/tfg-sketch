import time
import sys


def backspace(n):
    print('\r'*n, end='')                     # use '\r' to go back


def print_no_newline(string):
    if type(string) != type(''):
        string = str(string)
    print(string, end='\r'*len(string))

for i in range(101):                        # for 0 to 100
    s = [1,2,3]                   # string for output
    print_no_newline(s)                        # just print and flush
    time.sleep(0.2)  