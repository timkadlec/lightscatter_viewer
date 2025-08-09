import re
import numpy


def is_scientific_number(input):
    """
    Check whether a string represents a valid scientific number.

    A valid scientific number can be:
    - An integer: "42"
    - A decimal number: "3.14", ".5"
    - In scientific: "1.23e-4", "-2E5"

    Args:
        input (str): String to check.

    Returns:
        bool: True if the input is a valid scientific number, else False.
    """
    # Pattern tested through rexex101.com
    pattern = r"^[+-]?(?:\d+\.\d+|\.\d+|\d+)(?:[eE][+-]?\d+)?$"
    return bool(re.match(pattern, input))


def is_pair_of_numbers(line):
    """
    Determines if a line contains pair of valid scientific numbers.

    The numbers must be separated by whitespace.

    Args:
        line (str): Line to check.

    Returns:
        bool: True if the line is a pair of valid scientific numbers, else False.
    """
    parts = line.strip().split()
    if len(parts) != 2:
        return False
    return is_scientific_number(parts[0]) and is_scientific_number(parts[1])


def is_new_section(line):
    """
    Identify if the line marks start of new section.

    New section is defined by a line starting with '&'.

    Args:
        line (str): Line to check.

    Returns:
        bool: True if the line starts with '&', else False.
    """
    pattern = r"^[&]"
    return bool(re.match(pattern, line))


def equidistant_data_points(value, section):
    """
    Select exactly `value` equidistant data points from a section using numpy.

    This function uses `numpy.linspace` to generate evenly spaced integer
    indices across the range of available data points. This guarantees
    exactly `value` points when the section contains at least that many points.
    If the section contains fewer than `value` points, all points are returned.

    Args:
        value (int): The desired number of equidistant points.
        section (dict): A dictionary containing a 'data_points' list.
                        The function adds a 'data_points_equidistant' key
                        containing the selected points.

    Requirements:
        numpy: This function depends on NumPy for generating equidistant indices.
    """
    data = section["data_points"]
    n = len(data)

    if n <= value:
        section["data_points_equidistant"] = data
    else:
        indices = numpy.linspace(0, n - 1, value, dtype=int)
        section["data_points_equidistant"] = [data[i] for i in indices]


def process_spectrolight_dat_file(file_path):
    """
        Parse a Spectrolight .dat file into sections of metadata and data points.

        Sections are separated by a line containing only '&'. Within each section:
        - Lines containing pairs of scientific numbers are treated as data points.
        - All other lines are treated as metadata.

        Additionally, each section receives a 'data_points_equidistant' list
        containing up to 10 evenly spaced data points.

        Args:
            file_path (str): Path to the .dat file.

        Returns:
            list[dict]: A list of sections. Each section is a dict with:
                        - 'metadata' (list of str)
                        - 'data_points' (list of str) -- list of all datapoints, maybe useless?
                        - 'data_points_equidistant' (list of str)
        """
    sections = []
    current_section = {"metadata": [], "data_points": []}

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if is_new_section(line):
                # Save current section if some content in it
                if current_section["metadata"] or current_section["data_points"]:
                    sections.append(current_section)
                # start a new section if all datapoints have been looped through
                current_section = {"metadata": [], "data_points": []}

            # check if it is a pair of scientific numbers
            elif is_pair_of_numbers(line):
                current_section["data_points"].append(line)

            # add to metadata
            else:
                current_section["metadata"].append(line)

        # add the last section to the sections list []
        if current_section["metadata"] or current_section["data_points"]:
            sections.append(current_section)

    # process datapoint with equidistant - given equidistant value == 10
    for section in sections:
        equidistant_data_points(10, section)
    return sections
