import pytest
import os

# Find txt files starting with 'de_' in the root folder of the project
test_files = []
for file_name in os.listdir():
    if file_name.startswith("de_") and file_name.endswith(".txt"):
        test_files.append(file_name)


@pytest.mark.parametrize("file_name", test_files)
def test_that_number_of_opening_and_closing_braces_are_equal(file_name):
    with open(file_name, "r") as file:
        data = file.read()
        assert data.count("{") == data.count("}")
