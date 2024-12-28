import os
import subprocess  # nosec - This is a trusted command

# TODO: Ensure sub-process calls throw exceptions on error
# TODO: Write tests
# TODO: Look into reducing code logic and duplication in github workflow files

# Map folder names to their corresponding published_file_id
# At the time of writing, I have only found this to be working
# when the map is already uploaded to the workshop using the
# workshop_annotation_submit command in the game console.
published_file_id_map = {
    "de_ancient": "",  # TODO: Replace with actual Published File IDs
    "de_anubis": "",
    "de_dust2": "",
    "de_inferno": "",
    "de_mirage": "",
    "de_nuke": "3393679779",
    "de_overpass": "",
    "de_train": "",
    "de_vertigo": "",
}


# Function to generate the VDF content
def generate_vdf(output_path, content_folder, preview_file, title,
                 description, published_file_id):
    vdf_content = f"""
    "workshopitem"
    {
        "appid"            "730"
        "contentfolder"    "{content_folder}"
        "previewfile"      "{preview_file}"
        "visibility"       "0"
        "title"            "{title}"
        "description"      "{description}"
        "publishedfileid"  "{published_file_id}"
    }
    """

    with open(output_path, "w") as output:
        output.write(vdf_content)


# Iterate through sub-folders and upload items
base_folder = "local"
for folder_name in os.listdir(base_folder):
    map_name = folder_name
    map_path = os.path.join(base_folder, map_name)

    # file name is the same as the folder name with .txt
    file_name = map_name + ".txt"
    content_file = os.path.join(map_path, file_name)
    preview_file = os.path.join("assets", map_name, ".PNG")

    # Check if required files exist
    if not os.path.exists(content_file):
        raise FileNotFoundError(f"Content file missing for {map_name}.")
    if not os.path.exists(preview_file):
        raise FileNotFoundError(f"Preview file missing for {map_name}.")

    # Check if the folder name has a corresponding published_file_id
    if map_name not in published_file_id_map:
        raise KeyError(f"No published_file_id found for {map_name}.")

    # Generate metadata for the VDF
    title = f"zitrez {map_name} annotations"
    url = "https://github.com/ReneRebsdorf/CS2-annotations"
    description = f"Map annotations from {url}"
    published_file_id = published_file_id_map[map_name]

    # Create a temporary VDF file for this folder
    temp_vdf = os.path.join(map_path, "metadata.vdf")
    generate_vdf(
        temp_vdf, map_path, preview_file, title,
        description, published_file_id
    )

    # Run SteamCMD to upload the item
    subprocess.run([  # nosec - This is a trusted command
        os.environ['STEAM_CMD'],
        "+login",
        os.environ['STEAM_ACCOUNT_NAME'],
        "+workshop_build_item", temp_vdf,
        "+quit"
    ], check=True)
    print(f"Successfully uploaded {map_name}.")

    # Clean up temporary VDF file
    os.remove(temp_vdf)

print("All items processed.")