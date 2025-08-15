import re
import numpy


class InvalidDatFormatError(Exception):
    """Raised when a .dat file contains no valid numeric data pairs."""
    pass


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


def pick_equidistant_points(count, section):
    """
    Return up to `count` evenly spaced data points from a section.

    If the section contains fewer than `count` points, all points are returned.
    Otherwise, the function uses NumPy's `linspace` to calculate evenly spaced
    positions across the full range and returns exactly `count` points.

    Args:
        count (int): Number of equidistant points to select.
        section (dict): Dictionary containing a 'data_points' list.

    Returns:
        list: The selected equidistant data points.

    Dependencies:
        NumPy is required for generating the evenly spaced index positions.
    """

    points = section["data_points"]
    total = len(points)

    if total <= count:
        return points
    else:
        positions = numpy.linspace(start=0, stop=total - 1, num=count, dtype=int)
        return [points[pos] for pos in positions]


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

    with open(file_path, mode="r", encoding="utf-8") as f:
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
        if section["data_points"]:
            select_equidistant_data_points(10, section)
    return sections
