""""Test the annotations in the annotation files and the preview files."""

import os
import re

import keyvalues3 as kv3  # pylint: disable=import-error
import pytest  # pylint: disable=import-error

# Get all the preview files, which are PNGs with the map name as the filename
thumbnails = os.listdir("./assets/thumbnails/")

# Find txt files starting with 'de_' and assume them to be annotation files
test_files = []
annotations = []
annotation_collections = []
for dirpath, dirnames, filenames in os.walk("./local/"):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        if filename.startswith("de_"):
            file_path = os.path.join(dirpath, filename)
            test_files.append(file_path)
for file_name in test_files:
    map_specific_annotations = []
    dictionary = kv3.read(file_name)
    assert dictionary is not None

    # Add the dictionary (parsed map file, e.g. all of de_ancient.txt)
    # to the annotation collections
    annotation_collections.append(dictionary)

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
        anno_sub_type = map_specific_annotation["SubType"]
        is_valid_anno_sub_type = anno_sub_type in ["main", "aim_target"]
        if annotation_type == 'grenade' and is_valid_anno_sub_type:
            annotation_type = map_specific_annotation["Type"]
            name = map_specific_annotation["Title"]["Text"]
            position = map_specific_annotation["Position"]
            offset = map_specific_annotation["TextPositionOffset"]
            x = position[0] + offset[0]
            y = position[1] + offset[1]
            z = position[2] + offset[2]
            positions.append((anno_sub_type, name, x, y, z))
    for i, (anno_sub_type_first, name1, x1, y1, z1) in enumerate(positions):
        for anno_sub_type_second, name2, x2, y2, z2 in positions[i + 1:]:
            FIRST_NAME = f"{anno_sub_type_first}:{name1}"
            SECOND_NAME = f"{anno_sub_type_second}:{name2}"
            OVERLAP_TEXT = f"{FIRST_NAME} and {SECOND_NAME} overlap"
            ERROR_MESSAGE = f"{file_name}: {OVERLAP_TEXT}"
            # In a 3 dimensional plane, the distance between points
            # (X1, Y1, Z1) and (X2, Y2, Z2) is given by:
            # sqrt((X2 - X1)^2 + (Y2 - Y1)^2 + (Z2 - Z1)^2)
            squared = (x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2
            distance = squared ** 0.5
            assert distance > 1, ERROR_MESSAGE

assert len(annotations) > 0, "No annotations found in the test files"


@pytest.mark.parametrize("annotation_collection", annotation_collections)
def test_annotation_file_has_workshop_id(annotation_collection):
    """Test that the annotation file has a valid WorkshopSubmissionID."""
    map_name = annotation_collection.value["MapName"]

    error_msg = f"WorkshopSubmissionID not found in: {map_name}"
    assert "WorkshopSubmissionID" in annotation_collection.value, error_msg

    workshop_id = annotation_collection.value["WorkshopSubmissionID"]

    error_msg = f"WorkshopSubmissionID is empty in: {map_name}"
    assert workshop_id is not None, error_msg

    error_msg = f"WorkshopSubmissionID is 0 in: {map_name}"
    assert workshop_id not in ["0", ""], error_msg


def test_workshop_ids_are_unique():
    """Test that all WorkshopSubmissionIDs are unique."""
    ids = []
    for annotation_collection in annotation_collections:
        workshop_id = annotation_collection["WorkshopSubmissionID"]
        error_msg = f"Duplicate WorkshopSubmissionID: {workshop_id}"
        assert workshop_id not in ids, error_msg
        ids.append(workshop_id)


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_are_blue_or_yellow(annotation):
    """Test that all annotations are either blue or yellow."""
    if "Color" in annotation:
        a_type = annotation["Type"]
        a_sub_type = annotation["SubType"]
        a_title_text = "annotation has no title"
        if "Title" in annotation:
            if "Text" in annotation["Title"]:
                a_title_text = annotation["Title"]["Text"]
        e_msg = f"{a_type}/{a_sub_type}: {a_title_text}"
        color = annotation["Color"]
        ct_blue = [151, 201, 250]
        t_yellow = [255, 239, 111]
        assert color == ct_blue or color == t_yellow, e_msg


@pytest.mark.parametrize("annotation", annotations)
def test_annotations_have_no_placeholders(annotation):
    """Test that annotations have no placeholders."""
    desc_text = annotation["Desc"]["Text"]
    assert desc_text != "standing instructions"
    assert desc_text != "aim instructions"


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
    """
    Test that the preview file size is less than 1 MB.
    And matches the correct syntax for the map name.
    """
    err_msg = f"{thumbnail} is not a valid file name"
    assert re.match(r"^[a-z]{2}_\w+\.PNG$", thumbnail), err_msg
    size = os.path.getsize(f"./assets/thumbnails/{thumbnail}")
    size_megabytes = size / 1024 / 1024
    assert size_megabytes < 1, f"{thumbnail} is too large: {size_megabytes} MB"
