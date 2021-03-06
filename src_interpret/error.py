##
#   @file error.py
#
#   @brief Error handling and messages
#   @author Patrik Sehnoutek, xsehno01
#

import sys

class ErrorMessages:
    """Exit program with given code and print error message."""
    
    @staticmethod
    def exit_code(err_code):
        
        ERRORS = {
        10 : "ERROR: Wrong program argument or unknown combination of arguments!",
        11 : "ERROR: Cannot open file for reading!",
        31 : "ERORR: Invalid XML format of input file",
        32 : "ERROR: Unexpected XML structure",
        52 : "SEMATIC ERROR: ...",
        53 : "RUNTIME ERROR: Wrong types of operands",
        54 : "RUNTIME ERROR: Undefined variable",
        55 : "RUNTIME ERROR: Undefined frame",
        56 : "RUNTIME ERROR: Missing value",
        57 : "RUNTIME ERROR: Invalid operand value",
        58 : "RUNTIME ERROR: Invalid string operation"
        }

        print(ERRORS[err_code], file=sys.stderr)
        exit(err_code)