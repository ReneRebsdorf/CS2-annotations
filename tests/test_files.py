import pytest
import os
import keyvalues3 as kv3

# Find txt files starting with 'de_' in the root folder of the project
test_files = []
for file_name in os.listdir():
    if file_name.startswith("de_") and file_name.endswith(".txt"):
        test_files.append(file_name)


@pytest.mark.parametrize("file_name", test_files)
def test_that_parser_works(file_name):
    bt_config = kv3.read(file_name)
    assert bt_config is not None
