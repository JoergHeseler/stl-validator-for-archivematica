# Title: stl-validator
# Version: 1.0.0
# Publisher: NFDI4Culture
# Publication date: May 21, 2024
# License: CC BY 4.0
# Author: Joerg Heseler
# References: https://www.fabbers.com/tech/STL_Format#Sct_specs


from __future__ import print_function
import json
import sys
import math
import re

SUCCESS_CODE = 0
ERROR_CODE = 1
DEBUG = 1

warning_count = 0
errors_count = 0
first_error_message = ""
output_warnings = True 
# stop_on_first_error = False

######################## GEOMETRY FUNCTIONS ########################

def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def vector_magnitude(v):
    return math.sqrt(sum(x ** 2 for x in v))

def normalize_vector(v):
    magnitude = vector_magnitude(v)
    if magnitude == 0:
        return [0, 0, 0]
    return [x / magnitude for x in v]

def are_vectors_close(v1, v2, tol=1e-9):
    return all(abs(a - b) <= tol for a, b in zip(v1, v2))

def is_facet_oriented_correctly(vertex1, vertex2, vertex3, normal):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    calculated_normal = normalize_vector(cross_product(edge1, edge2))
    normal = normalize_vector(normal)
    return are_vectors_close(calculated_normal, normal)

def ensure_counterclockwise(vertex1, vertex2, vertex3, normal):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    calculated_normal = cross_product(edge1, edge2)
    if dot_product(calculated_normal, normal) < 0:
        vertex2, vertex3 = vertex3, vertex2
    return vertex1, vertex2, vertex3

######################## LINE FUNCTIONS ########################

y = 0
lines = []

def print_warning(expected, got = None):
    global y
    global warning_count
    global output_warnings
    warning_count += 1
    if output_warnings:
        if got:
            print(f"Warning on line {y + 1}: Expected '{expected}' but got '{got.strip()}'.")
        else:
            print(f"Warning on line {y + 1}: {expected}.")
    
def print_error(expected, got):
    global y
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

def get_current_line():
    global y
    global lines
    return lines[y]

def skip_empty_lines():
    global y
    global lines
    while len(lines) > y + 1 and lines[y].strip() == "":
        print_warning("Line is empty")
        y += 1

def init_line():
    global y
    global lines
    y = 0
    skip_empty_lines()

def go_to_next_line():
    global y
    global lines
    y += 1
    skip_empty_lines()

######################## VALIDATION FUNCTIONS ########################

class STLValidatorException(Exception):
    
    def __init__(self, result):
        super().__init__(result)
        if DEBUG:
            print(result)
        
    # def __init__(self, y, expected, got):
        # super().__init__(result)
        # if DEBUG:
            # print(result)

def format_event_outcome_detail_note(format, version, result):
    note = 'format="{}";'.format(format)
    if version is not None:
        note = note + ' version="{}";'.format(version)
    if result is not None:
        note = note + ' result="{}"'.format(result)

    return note

######################## MAIN ########################

def main(target):
    global y
    global lines
    try:
        with open(target, 'r') as file:
            lines = [re.sub(r'\s+', ' ' , line.strip()) for line in file.readlines()]
        
        init_line()

        if not get_current_line().startswith("solid"):
            print_error("solid", get_current_line())     
        if not re.search(f"^solid [^\n]+$", get_current_line()):
            print_warning("solid <string>", get_current_line())
            name = ""
        else:
            name = str(get_current_line()[6:]).lstrip()
        go_to_next_line()
        
        # The notation, “{…}+,” means that the contents of the brace brackets
        # can be repeated one or more times.
        # --> Changed by the author to “{…}*”, meaning that the contents of the
        # brace brackets can be repeated none, one or more times, to support
        # empty scenes as many programs are able to export.
        total_facet_count = (len([line for line in lines if line.strip()]) - 2) // 7
        # all_vertex_coordinates_are_positive = True
        # all_facets_normals_are_correct = True
        # all_vertices_of_facets_are_ordered_clockwise = True

        for _ in range(total_facet_count):
            if not re.search(f"^facet normal -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                print_error("facet normal <float> <float> <float>", get_current_line())
            go_to_next_line()
            if not "outer loop" == get_current_line():
                print_error("outer loop", get_current_line())
            go_to_next_line()

            normal = list(map(float, get_current_line().split()[2:]))
            vertices = []
            for j in range(3):
            
                # A facet normal coordinate may have a leading minus sign; 
                # a vertex coordinate may not.
                # --> Changed by the author to vertex coordinates may have a
                # leading minus, to support negative vertices to support many
                # programs are able to export
                if not re.search(f"^vertex -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                    print_error("vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
                # if not re.search(f"^vertex \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                    # print_warning("vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
                vertex = list(map(float, get_current_line().split()[1:]))
                go_to_next_line()
                if any(coord < 0 for coord in vertex):
                    # all_vertex_coordinates_are_positive = False
                    print_warning("Not all vertices have positive values")
                vertices.append(vertex)
            if not is_facet_oriented_correctly(vertices[0], vertices[1], vertices[2], normal):
                print_warning("Facet is not oriented correctly")
                # all_facets_normals_are_correct = False
            if not ensure_counterclockwise(vertices[0], vertices[1], vertices[2], normal):
                print_warning("Vertices of facet are not ordered clockwise")
                # all_vertices_of_facets_are_ordered_clockwise = False
            if not "endloop" == get_current_line():
                print_error("endloop", get_current_line())
            go_to_next_line()
            if not "endfacet" == get_current_line():
                print_error("endfacet", get_current_line())
            go_to_next_line()
        if not re.search("^endsolid", get_current_line()):
            print_error("endsolid", get_current_line())
        if name != "":
            if not f"endsolid {name}" == get_current_line():
                print_error(f"endsolid {name}", get_current_line())
        go_to_next_line()
        
        
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
    output_warnings = not any(arg.strip().lower() == "--output_no_warnings" for arg in sys.argv)
    target = sys.argv[1]
    sys.exit(main(target))
