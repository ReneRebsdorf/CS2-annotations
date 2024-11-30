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
    assert dict is not None

    # Get the annotations where the key is MapAnnotationNodeX
    for key in dict:
        if key.startswith("MapAnnotationNode"):
            annotations.append(dict[key])
            file_annotations.append(dict[key])
    file_annotation_ids = [item["Id"] for item in file_annotations]

    # Tests for each file
    positions = []
    for annotation in file_annotations:
        master_node_id = ""
        if "MasterNodeId" in annotation:
            master_node_id = annotation["MasterNodeId"]
        if master_node_id != "":
            assert master_node_id in file_annotation_ids
        if annotation["Type"] == 'grenade' and annotation["SubType"] == "main":
            name = annotation["Title"]["Text"]
            position = annotation["Position"]
            offset = annotation["TextPositionOffset"]
            x = position[0] + offset[0]
            y = position[1] + offset[1]
            z = position[2] + offset[2]
            positions.append((name, x, y, z))
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            name1, x1, y1, z1 = positions[i]
            name2, x2, y2, z2 = positions[j]
            overlap_text = f"{positions[i]} and {positions[j]} overlap"
            error_message = f"{file_name}: {overlap_text}"
            # In a 3 dimensional plane, the distance between points
            # (X1, Y1, Z1) and (X2, Y2, Z2) is given by:
            # sqrt((X2 - X1)^2 + (Y2 - Y1)^2 + (Z2 - Z1)^2)
            squared = ((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            distance = squared ** 0.5
            assert distance > 1, error_message

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
