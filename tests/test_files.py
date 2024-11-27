import pytest
import os
import keyvalues3 as kv3

# Find txt files starting with 'de_' in the root folder of the project
test_files = []
for file_name in os.listdir():
    if file_name.startswith("de_") and file_name.endswith(".txt"):
        # Test the file can parse
        dict = kv3.read(file_name)

        @pytest.mark.parametrize("dict", dict)
        def test_that_parser_works(dict):
            assert dict is not None

        # Get the annotations where the key is MapAnnotationNodeX
        annotations = []
        for key in dict:
            if key.startswith("MapAnnotationNode"):
                annotations.append(dict[key])

        # Test the annotations
        @pytest.mark.parametrize("annotation", annotations)
        def test_annotations_are_blue_or_yellow(annotation):
            color = annotation["color"]
            assert color == [151, 201, 250] or color == [234, 191, 86]

        def test_annotations_have_no_placeholders(annotation):
            placeHolderKey = annotation["Desc"]["Text"] 
            assert placeHolderKey != "standing instructions"
            assert placeHolderKey != "aim instructions"
