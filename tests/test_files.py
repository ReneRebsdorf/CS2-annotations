import pytest
import os
import keyvalues3 as kv3

# Find txt files starting with 'de_' in the root folder of the project
test_files = []
annotations = []
for dirpath, dirnames, filenames in os.walk("./local/"):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        if filename.startswith("de_"):
            file_path = os.path.join(dirpath, filename)
            test_files.append(file_path)
for file_name in test_files:
    file_annotations = []
    dict = kv3.read(file_name)

    def test_that_parser_works():
        assert dict is not None

    # Get the annotations where the key is MapAnnotationNodeX
    for key in dict:
        if key.startswith("MapAnnotationNode"):
            annotations.append(dict[key])
            file_annotations.append(dict[key])
    file_annotation_ids = [item["Id"] for item in file_annotations]

    # Tests for each file
    for annotation in file_annotations:
        master_node_id = ""
        if "MasterNodeId" in annotation:
            master_node_id = annotation["MasterNodeId"]
        if master_node_id != "":
            assert master_node_id in file_annotation_ids
assert len(annotations) > 0, "No annotations found in the test files"


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_are_blue_or_yellow(annotation):
    if "Color" in annotation:
        color = annotation["Color"]
        ct_blue = [151, 201, 250]
        t_yellow = [255, 239, 111]
        assert color == ct_blue or color == t_yellow


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_have_no_placeholders(annotation):
    placeHolderKey = annotation["Desc"]["Text"]
    assert placeHolderKey != "standing instructions"
    assert placeHolderKey != "aim instructions"


def test_annotation_ids_are_unique():
    ids = []
    for annotation in annotations:
        id = annotation["Id"]
        assert id not in ids
        ids.append(id)
