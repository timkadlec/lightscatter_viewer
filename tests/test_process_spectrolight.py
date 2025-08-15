# tests/test_process_spectrolight.py
import os
import numpy as np
import pytest

from process_spectrolight import (
    is_scientific_number,
    is_pair_of_numbers,
    is_new_section,
    pick_equidistant_points,
    process_spectrolight_dat_file,
    InvalidDatFormatError,
)


# ---------- is_scientific_number ----------

@pytest.mark.parametrize("text", [
    "0",
    "42",
    "-7",
    "3.14",
    ".5",
    "+.5",
    "-.75",
    "1e5",
    "-2E5",
    "1.23e-4",
    "+6.02E23",
])
def test_is_scientific_number_valid(text):
    assert is_scientific_number(text) is True


@pytest.mark.parametrize("text", [
    "",
    "abc",
    "1e",
    "e10",
    "1.2.3",
    "+.",
    "--1",
    "NaN",
    "inf",
    "+inf",
    "1,2",  # comma not allowed by the regex
    " 42 ",  # leading/trailing spaces (caller should strip)
])
def test_is_scientific_number_invalid(text):
    assert is_scientific_number(text) is False


# ---------- is_pair_of_numbers ----------

@pytest.mark.parametrize("line", [
    "1 2",
    "3.14 .5",
    "-1e3 2E-2",
    "\t1\t2\t",    # tabs are whitespace
    "+.5 -2.5e-3",
])
def test_is_pair_of_numbers_true(line):
    assert is_pair_of_numbers(line) is True


@pytest.mark.parametrize("line", [
    "",
    "1",
    "1 2 3",
    "1, 2",
    "one two",
    "1e ",      # second token missing
    "  42  ",   # single token after strip/split
])
def test_is_pair_of_numbers_false(line):
    assert is_pair_of_numbers(line) is False


# ---------- is_new_section ----------

def test_is_new_section_true_exact_ampersand():
    assert is_new_section("&") is True

def test_is_new_section_true_starts_with_ampersand():
    # Current implementation treats any line *starting with* '&' as a new section
    assert is_new_section("& section header") is True

def test_is_new_section_false_when_space_before_ampersand():
    assert is_new_section(" &") is False

def test_is_new_section_false_no_ampersand():
    assert is_new_section("no section here") is False


# ---------- pick_equidistant_points ----------

def test_pick_equidistant_points_returns_all_when_fewer_than_count():
    section = {"data_points": [f"{i} {i+1}" for i in range(3)]}
    out = pick_equidistant_points(10, section)
    assert out == section["data_points"]  # returns all

def test_pick_equidistant_points_exactly_count_when_more_than_count():
    n = 25
    count = 10
    points = [f"{i} {i+0.1}" for i in range(n)]
    section = {"data_points": points}

    out = pick_equidistant_points(count, section)
    assert len(out) == count

    # Expected indices produced by current implementation:
    expected_idx = np.linspace(start=0, stop=n - 1, num=count, dtype=int)
    expected = [points[i] for i in expected_idx]
    assert out == expected

def test_pick_equidistant_points_includes_first_and_last():
    points = [f"{i} {i+0.1}" for i in range(50)]
    section = {"data_points": points}
    out = pick_equidistant_points(10, section)
    assert out[0] == points[0]
    assert out[-1] == points[-1]


# ---------- process_spectrolight_dat_file ----------

def _write(tmp_path, name, contents: str):
    p = tmp_path / name
    p.write_text(contents, encoding="utf-8")
    return str(p)

def test_process_parses_sections_and_datapoints(tmp_path):
    # Mix of metadata lines and numeric pairs with two section separators.
    # Note: is_new_section() returns True for any line starting with '&'
    contents = """Header metadata line
&
Meta A
1 2
3.0e0 4.5E-1
&
Another meta
-1.2 3
.5 -2E5
"""
    path = _write(tmp_path, "sample.dat", contents)
    sections = process_spectrolight_dat_file(path)

    # We expect three sections: before first &, between &s, and after second &
    assert len(sections) == 3

    # Section 0: only metadata (header line)
    assert sections[0]["metadata"] == ["Header metadata line"]
    assert sections[0]["data_points"] == []
    assert "data_points_equidistant" not in sections[0]

    # Section 1: has two data point lines and meta 'Meta A'
    assert "Meta A" in sections[1]["metadata"]
    assert sections[1]["data_points"] == ["1 2", "3.0e0 4.5E-1"]
    # equidistant list should exist and equal the original (<= 10 points)
    assert sections[1]["data_points_equidistant"] == sections[1]["data_points"]

    # Section 2: has two numeric lines and one meta
    assert "Another meta" in sections[2]["metadata"]
    assert sections[2]["data_points"] == ["-1.2 3", ".5 -2E5"]
    assert sections[2]["data_points_equidistant"] == sections[2]["data_points"]

def test_process_raises_when_no_numeric_pairs(tmp_path):
    contents = """Only metadata
and more metadata
& Section but no numeric pairs
Still not numbers"""
    path = _write(tmp_path, "no_pairs.dat", contents)
    with pytest.raises(InvalidDatFormatError):
        process_spectrolight_dat_file(path)

def test_process_creates_equidistant_max_10_when_many_points(tmp_path):
    # Create a section with > 10 numeric lines to force down-selection
    numeric_lines = "\n".join(f"{i} {i+0.1}" for i in range(37))
    contents = f"""Meta before
&
Meta with many numbers
{numeric_lines}
"""
    path = _write(tmp_path, "many_points.dat", contents)
    sections = process_spectrolight_dat_file(path)

    # Find the section that actually contains points (> 10)
    sec = next(s for s in sections if len(s["data_points"]) > 10)

    assert len(sec["data_points"]) == 37
    assert "data_points_equidistant" in sec
    assert len(sec["data_points_equidistant"]) == 10

    # Check selection equals current numpy.linspace(int) behaviour
    expected_idx = np.linspace(0, 36, 10, dtype=int)
    expected = [sec["data_points"][i] for i in expected_idx]
    assert sec["data_points_equidistant"] == expected
