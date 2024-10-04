# Title: stl-validator
# Version: 1.0.0
# Publisher: NFDI4Culture
# Publication date: 2024, May 21th
# License: CC BY 4.0
# Author: Joerg Heseler
# References: https://www.fabbers.com/tech/STL_Format#Sct_specs


from __future__ import print_function
import json
import subprocess
import sys
from lxml import etree
import re

SUCCESS_CODE = 0
ERROR_CODE = 1
DEBUG = 1

class STLValidatorException(Exception):
    
    def __init__(self, result):
        super().__init__(result)
        if DEBUG:
            print(result)
        
    # def __init__(self, y, expected, got):
        # super().__init__(result)
        # if DEBUG:
            # print(result)

warning_count = 0
errors_count = 0
first_error_message = ""
# stop_on_first_error = False

def print_warning(y, expected, got):
    global warning_count
    print(f"Warning on line {y + 1}: Expected '{expected}' but got '{got.strip()}'.")
    warning_count += 1
    
def print_error(y, expected, got):
    global errors_count
    global first_error_message
    global stop_on_first_error
    if first_error_message == "":
        first_error_message = f"line {y + 1}: Expected '{expected}' but got '{got.strip()}'."
    error_message = f"Error on {first_error_message}"
    errors_count += 1
    # if stop_on_first_error:
    raise STLValidatorException(error_message)
    # else:
    # print(error_message)


def format_event_outcome_detail_note(format, version, result):
    note = 'format="{}";'.format(format)
    if version is not None:
        note = note + ' version="{}";'.format(version)
    if result is not None:
        note = note + ' result="{}"'.format(result)

    return note

def main(target):
    try:
        with open(target, 'r') as file:
            lines = file.readlines()
                                 
        lines = [line for line in lines if line.strip()]
        
        y = 0
        if not lines[y].startswith("solid"):
            print_error(y, "solid", lines[y])     
        if not re.search(f"^solid [^\n]+$", lines[y]):
            print_warning(y, "solid <string>", lines[y])
            name = ""
        else:
            name = str(lines[y][6:]).lstrip()
        y += 1
        
        # The notation, “{…}+,” means that the contents of the brace brackets
        # can be repeated one or more times.
        # --> Changed by the author to “{…}*”, meaning that the contents of the
        # brace brackets can be repeated none, one or more times, to support
        # empty scenes as many programs are able to export.
        for _ in range(int((len(lines) - 2) / 7)):
            if not re.search(f"^facet normal -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", lines[y]):
                print_error(y, "facet normal <float> <float> <float>", lines[y])
            y += 1
            if not "outer loop" == lines[y]:
                print_error(y, "outer loop", lines[y])
            y += 1
            for _ in range(3):
            
                # A facet normal coordinate may have a leading minus sign; 
                # a vertex coordinate may not.
                # --> Changed by the author to vertex coordinates may have a
                # leading minus, to support negative vertices to support many
                # programs are able to export
                if not re.search(f"^vertex -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", lines[y]):
                    print_error(y, "vertex <unsigned float> <unsigned float> <unsigned float>", lines[y])
                if not re.search(f"^vertex \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)?$", lines[y]):
                    print_warning(y, "vertex <unsigned float> <unsigned float> <unsigned float>", lines[y])
                y += 1
            if not "endloop" == lines[y]:
                print_error(y, "endloop", lines[y])
            y += 1
            if not "endfacet" == lines[y]:
                print_error(y, "endfacet", lines[y])
            y += 1
        if not re.search("^endsolid", lines[y]):
            print_error(y, "endsolid", lines[y])
        if name != "":
            if not f"endsolid {name}" == lines[y]:
                print_error(y, f"endsolid {name}", lines[y])
        y += 1
        
        
        if errors_count >= 1:
            raise STLValidatorException(f"STL file validation failed, errors: {errors_count}, warnings: {warning_count}, first error on {first_error_message}")

            
        format = "STL"
        version = "1.0"
        
        note = format_event_outcome_detail_note(format, version, f"errors: {errors_count}, warnings: {warning_count}")

        print(
            json.dumps(
                {
                    "eventOutcomeInformation": "pass",
                    "eventOutcomeDetailNote": note,
                    "stdout": target + " validates.",
                }
            )
        )

        return SUCCESS_CODE
    except STLValidatorException as e:
        print(
            json.dumps(
                {
                    "eventOutcomeInformation": "fail",
                    "eventOutcomeDetailNote": str(e),
                    "stdout": None,
                }
            ),
            file=sys.stderr,
        )
        return ERROR_CODE

if __name__ == "__main__":
    target = sys.argv[1]
    sys.exit(main(target))
