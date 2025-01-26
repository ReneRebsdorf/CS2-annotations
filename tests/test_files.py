""""Test the annotations in the annotation files and the preview files."""

import os
import re

import keyvalues3 as kv3  # pylint: disable=import-error
import pytest  # pylint: disable=import-error

# Get all the preview files, which are PNGs with the map name as the filename
thumbnails = os.listdir("./assets/")
thumbnails = [f for f in thumbnails if f.endswith(".PNG")]
thumbnails = [f for f in thumbnails if f.startswith("de_")]

# Find txt files starting with 'de_' and assume them to be annotation files
test_files = []
annotations = []
for dirpath, dirnames, filenames in os.walk("./local/"):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        if filename.startswith("de_"):
            file_path = os.path.join(dirpath, filename)
            test_files.append(file_path)
for file_name in test_files:
    map_specific_annotations = []
    dictionary = kv3.read(file_name)
    assert dictionary is not None

    # Get the annotations where the key is MapAnnotationNodeX
    for key in dictionary:
        if key.startswith("MapAnnotationNode"):
            annotations.append(dictionary[key])
            map_specific_annotations.append(dictionary[key])
    map_specific_annotation_ids = [
        item["Id"] for item in map_specific_annotations
    ]

    # Tests for each file
    positions = []
    for map_specific_annotation in map_specific_annotations:
        MASTER_NODE_ID = ""
        if "MasterNodeId" in map_specific_annotation:
            MASTER_NODE_ID = map_specific_annotation["MasterNodeId"]
        if MASTER_NODE_ID != "":
            assert MASTER_NODE_ID in map_specific_annotation_ids
        annotation_type = map_specific_annotation["Type"]
        annotation_sub_type = map_specific_annotation["SubType"]
        if annotation_type == 'grenade' and annotation_sub_type == "main":
            name = map_specific_annotation["Title"]["Text"]
            position = map_specific_annotation["Position"]
            offset = map_specific_annotation["TextPositionOffset"]
            x = position[0] + offset[0]
            y = position[1] + offset[1]
            z = position[2] + offset[2]
            positions.append((name, x, y, z))
    for i, (name1, x1, y1, z1) in enumerate(positions):
        for name2, x2, y2, z2 in positions[i + 1:]:
            overlap_text = f"{name1} and {name2} overlap"
            error_message = f"{file_name}: {overlap_text}"
            # In a 3 dimensional plane, the distance between points
            # (X1, Y1, Z1) and (X2, Y2, Z2) is given by:
            # sqrt((X2 - X1)^2 + (Y2 - Y1)^2 + (Z2 - Z1)^2)
            squared = (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2
            distance = squared ** 0.5
            assert distance > 1, error_message

assert len(annotations) > 0, "No annotations found in the test files"


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_are_blue_or_yellow(annotation):
    """Test that all annotations are either blue or yellow."""
    if "Color" in annotation:
        color = annotation["Color"]
        ct_blue = [151, 201, 250]
        t_yellow = [255, 239, 111]
        assert color == ct_blue or color == t_yellow


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_have_no_placeholders(annotation):
    """Test that annotations have no placeholders."""
    place_holder_key = annotation["Desc"]["Text"]
    assert place_holder_key != "standing instructions"
    assert place_holder_key != "aim instructions"


def test_annotation_ids_are_unique():
    """Test that all annotation IDs are unique."""
    ids = []
    for annotation in annotations:
        this_id = annotation["Id"]
        assert this_id not in ids
        ids.append(this_id)


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_have_no_empty_title(annotation):
    """Test that annotations have no empty titles."""
    this_type = annotation["Type"]
    if this_type in ["spot", "text", "line"]:
        return
    sub_type = annotation["SubType"]
    is_destination = sub_type == "destination"
    if is_destination:
        return
    title = annotation["Title"]["Text"]
    assert title != "", f"Empty title for {this_type}/{sub_type}"


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_setpos_exact_has_no_overlap_with_z_position(annotation):
    """Test that setpos_exact annotations have no overlap with z position."""
    # Get the z-position of the annotation from the Position key
    z_position = annotation["Position"][2]

    # Get the description of the annotation, and check if it is a setpos_exact
    description = annotation["Desc"]["Text"]
    # Check the Desc.Text is potentially a valid setpos_exact command
    setpos_exact_positions = None
    if description.startswith("setpos_exact"):
        # Get characters after the "setpos_exact "
        desc_positions = description[13:]
        # Split the string into a list of strings by the " " character
        # This gets us x, y, and z
        setpos_exact_positions = re.split(r" ", desc_positions)
        # Check the length is as expected
        if len(setpos_exact_positions) == 3:
            setpos_exact_z = int(setpos_exact_positions[-1])
            assert setpos_exact_z > z_position


@pytest.mark.parametrize("annotation", annotations)
def test_grenade_type(annotation):
    """Test that grenade annotations have a valid grenade type."""
    if annotation["Type"] == 'grenade':
        if annotation["SubType"] == "main":
            grenade_type = annotation["GrenadeType"].lower()
            valid_grenade_types = [
                "smoke",
                "flash",
                "he",
                "molotov",
                "incendiary",
                "decoy"
            ]
            assert grenade_type in valid_grenade_types


@pytest.mark.parametrize("thumbnail", thumbnails)
def test_preview_file_size(thumbnail):
    """Test that the preview file size is less than 1 MB."""
    size = os.path.getsize(f"./assets/{thumbnail}")
    size_megabytes = size / 1024 / 1024
    assert size_megabytes < 1, f"{thumbnail} is too large: {size_megabytes} MB"
