# Title: stl-validator
# Version: 1.0.0
# Publisher: NFDI4Culture
# Publication date: December 5, 2024
# License: CC BY-SA 4.0
# Author: Joerg Heseler
# References: https://www.fabbers.com/tech/STL_Format#Sct_specs

from __future__ import print_function
import json
import os
import struct
import sys
import math
import re

SUCCESS_CODE = 0
ERROR_CODE = 1
DEBUG = 1
strict_mode = True
ERROR = True
WARNING = False

warning_count = 0
error_count = 0
first_error_message = ""
output_detailed_warnings = False 
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

# def is_facet_oriented_correctly(vertex1, vertex2, vertex3, normal):
#     edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
#     edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
#     calculated_normal = normalize_vector(cross_product(edge1, edge2))
#     normal = normalize_vector(normal)
#     return are_vectors_close(calculated_normal, normal)

# def ensure_counterclockwise(vertex1, vertex2, vertex3, normal):
#     edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
#     edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
#     calculated_normal = cross_product(edge1, edge2)
#     if dot_product(calculated_normal, normal) < 0:
#         vertex2, vertex3 = vertex3, vertex2
#     return vertex1, vertex2, vertex3

def is_counterclockwise(vertex1, vertex2, vertex3, normal):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    calculated_normal = cross_product(edge1, edge2)
    return dot_product(calculated_normal, normal) > 0


######################## LINE FUNCTIONS ########################

line_index = 0
lines = []

def handle_error_with_line_index(type, expected, got = None):
    global line_index, error_count, warning_count, output_detailed_warnings
    if type == ERROR:
        # Error
        error_count += 1
        if got:
            error_message = f"Error on line {line_index + 1}: Expected '{expected}' but got '{got.strip()}'."
        else:
            error_message = f"Error on line {line_index + 1}: {expected}."
        raise STLValidatorException(error_message)
    elif type == WARNING:
        # Warning
        warning_count += 1
        if output_detailed_warnings:
            if got:
                print(f"Warning on line {line_index + 1}: Expected '{expected}' but got '{got.strip()}'.")
            else:
                print(f"Warning on line {line_index + 1}: {expected}.")

def handle_error_with_file_pos(type, pos, expected, got = None):
    global error_count, warning_count, output_detailed_warnings
    if type == ERROR:
        # Error
        error_count += 1
        if got:
            error_message = f"Error on position {pos}: Expected '{expected}' but got '{got.strip()}'."
        else:
            error_message = f"Error on position {pos}: {expected}."
        raise STLValidatorException(error_message)
    elif type == WARNING:
        # Warning
        warning_count += 1
        if output_detailed_warnings:
            if got:
                print(f"Warning on position {pos}: Expected '{expected}' but got '{got.strip()}'.")
            else:
                print(f"Warning on position {pos}: {expected}.")


def get_current_line():
    global line_index, lines
    return lines[line_index]

def skip_empty_lines():
    global line_index
    global lines
    while len(lines) > line_index + 1 and lines[line_index].strip() == "":
        handle_error_with_line_index(WARNING, "Line is empty")
        line_index += 1

def init_line():
    global line_index, lines
    line_index = 0
    skip_empty_lines()

def go_to_next_line():
    global line_index, lines
    line_index += 1
    skip_empty_lines()

######################## STL FUNCTIONS ########################

def is_binary_stl(file_path):
    # Check if the STL file is binary or ASCII.
    with open(file_path, 'rb') as file:
        file_size = os.path.getsize(file_path)
        file.read(80).decode('ascii', errors='ignore')
        try:
            triangle_count = struct.unpack('<I', file.read(4))[0]
        except struct.error:
            return False
        return 80 + 4 + 50 * triangle_count == file_size

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

def validate_binary_stl_file(file_path):
    global error_count, warning_count, first_error_message, strict_mode
    with open(file_path, 'rb') as file:
        file.read(80) # Header
        triangle_count = struct.unpack('<I', file.read(4))[0]
        
        for i in range(triangle_count):
            normal = struct.unpack('<3f', file.read(12))
            vertex1 = struct.unpack('<3f', file.read(12))
            vertex2 = struct.unpack('<3f', file.read(12))
            vertex3 = struct.unpack('<3f', file.read(12))
            attr_byte_count = struct.unpack('<H', file.read(2))[0]
            pos = 84 + i * 50

            if any(coord < 0 for coord in vertex1 + vertex2 + vertex3):
                handle_error_with_file_pos(WARNING or strict_mode, pos, "Not all vertices of this facet have positive values")

            if not is_counterclockwise(vertex1, vertex2, vertex3, normal):
                handle_error_with_line_index(WARNING or strict_mode, "Vertices of this facet are not ordered counterclockwise")

            if any(math.isnan(v) for v in normal + vertex1 + vertex2 + vertex3):
                handle_error_with_file_pos(ERROR, pos, "File contains NaN values in normal or vertex coordinates")
            
            if attr_byte_count != 0:
                handle_error_with_file_pos(ERROR, pos, f"Attribute byte count should be '0', but got '{attr_byte_count}'")
                

def format_event_outcome_detail_note(format, version, result):
    note = 'format="{}";'.format(format)
    if version is not None:
        note = note + ' version="{}";'.format(version)
    if result is not None:
        note = note + ' result="{}"'.format(result)

    return note


def validate_ascii_stl_file(target):
    global line_index, lines, strict_mode
    with open(target, 'r') as file:
        lines = [re.sub(r'\s+', ' ' , line.strip()) for line in file.readlines()]
    
    init_line()

    if not get_current_line().startswith("solid"):
        handle_error_with_line_index(ERROR, "solid", get_current_line())     
    if not re.search(f"^solid [^\n]+$", get_current_line()):
        handle_error_with_line_index(WARNING, "solid <string>", get_current_line())
        solid_name = ""
    else:
        solid_name = str(get_current_line()[6:]).lstrip()
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
            handle_error_with_line_index(ERROR, "facet normal <float> <float> <float>", get_current_line())
        normal = list(map(float, get_current_line().split()[2:]))
        go_to_next_line()
        if not "outer loop" == get_current_line():
            handle_error_with_line_index(ERROR, "outer loop", get_current_line())
        go_to_next_line()

        vertices = []
        for j in range(3):
        
            # A facet normal coordinate may have a leading minus sign; 
            # a vertex coordinate may not.
            # --> Changed by the author to vertex coordinates may have a
            # leading minus, to support negative vertices to support many
            # programs are able to export
            if not re.search(f"^vertex -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                handle_error_with_line_index(ERROR, "vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
            # if not re.search(f"^vertex \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                # print_warning("vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
            vertex = list(map(float, get_current_line().split()[1:]))
            go_to_next_line()
            if any(coord < 0 for coord in vertex):
                # all_vertex_coordinates_are_positive = False
                handle_error_with_line_index(WARNING or strict_mode, "Not all vertice coordinates have positive values")
            vertices.append(vertex)
        # if not is_facet_oriented_correctly(vertices[0], vertices[1], vertices[2], normal):
        #     print_warning("Facet is not oriented correctly")
        #     # all_facets_normals_are_correct = False
        if not is_counterclockwise(vertices[0], vertices[1], vertices[2], normal):
            handle_error_with_line_index(WARNING or strict_mode, "Vertices of this facet are not ordered counterclockwise")
            # all_vertices_of_facets_are_ordered_clockwise = False
        if not "endloop" == get_current_line():
            handle_error_with_line_index(ERROR, "endloop", get_current_line())
        go_to_next_line()
        if not "endfacet" == get_current_line():
            handle_error_with_line_index(ERROR, "endfacet", get_current_line())
        go_to_next_line()
    if not re.search("^endsolid", get_current_line()):
        handle_error_with_line_index(ERROR, "endsolid", get_current_line())
    if solid_name != "":
        if not f"endsolid {solid_name}" == get_current_line():
            handle_error_with_line_index(WARNING or strict_mode, f"endsolid {solid_name}", get_current_line())
    go_to_next_line()
    

def validate_stl_file(file_path):
    global error_count, warning_count, first_error_message
    try:
        if is_binary_stl(file_path):
            validate_binary_stl_file(file_path)
            version = 'binary'
        else:
            validate_ascii_stl_file(file_path)
            version = 'ASCII'

        if error_count > 0:
            raise STLValidatorException(f"Validation failed: errors={error_count}, warnings={warning_count}, first error: {first_error_message}")
        
        format = 'STL (Standard Tessellation Language)'

        note = format_event_outcome_detail_note(format, version, f"errors: {error_count}, warnings: {warning_count}")

        print(
            json.dumps(
                {
                    "eventOutcomeInformation": "pass",
                    "eventOutcomeDetailNote": note,
                    "stdout": file_path + " validates.",
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


######################## MAIN FUNCTION ########################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'STL Validator, version 1.0.0')
        print()
        print(f'This script validates ASCII and binary STL files according to the specifications of https://www.fabbers.com/tech/STL_Format.')
        print()
        print(f'Usage: python stl-validator.py <stl-file> [options]')
        print()        
        print(f'--warnings    prints all warning information to standard output')
        print(f'--tolerant    passes validation even if the vertex coordinates are negative, the vertices of each facet are not')
        print(f'              arranged counterclockwise, or the solid name differs from the endsolid name.')
        sys.exit(0)
    output_detailed_warnings = any(arg.strip().lower() == "--warnings" for arg in sys.argv)
    if any(arg.strip().lower() == "--tolerant" for arg in sys.argv):
        strict_mode = False
    target = sys.argv[1]
    sys.exit(validate_stl_file(target))
