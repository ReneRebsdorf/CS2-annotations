"""This script uploads the annotations to the Steam Workshop"""

import argparse
import os
import subprocess  # nosec - Used to run SteamCMD


def generate_vdf(output_path, content_folder, preview_file, title,
                 description, published_file_id):
    """Function to generate the VDF content"""

    # Import the template file content
    working_dir = os.getcwd()
    template_file_name = "workshop-metadata-template.vdf"
    template_file_path = os.path.join(working_dir, "src", template_file_name)
    with open(template_file_path, "r", encoding="utf-8") as file:
        vdf_content = file.read()

    # Modify placeholders
    vdf_content = vdf_content.replace("{content_folder}", content_folder)
    vdf_content = vdf_content.replace("{preview_file}", preview_file)
    vdf_content = vdf_content.replace("{title}", title)
    vdf_content = vdf_content.replace("{description}", description)
    vdf_content = vdf_content.replace("{published_file_id}", published_file_id)

    # Write the modified content to the output file
    with open(output_path, "w", encoding="utf-8") as output:
        output.write(vdf_content)


if __name__ == "__main__":
    # Map folder names to their corresponding published_file_id
    # At the time of writing, I have only found this to be working
    # when the map is already uploaded to the workshop using the
    # workshop_annotation_submit command in the game console.
    published_file_id_map = {
        "de_ancient": "3397846803",
        "de_anubis": "3397845762",
        "de_dust2": "3397851092",
        "de_inferno": "3397850337",
        "de_mirage": "3397848956",
        "de_nuke": "3393679779",
        "de_overpass": "3397844011",
        "de_train": "3397841296",
        "de_vertigo": "3397844974",
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--steam_cmd",
        help="Path to the SteamCMD executable",
        required=True
    )
    parser.add_argument(
        "--steam_account_name",
        help="Steam account name to login with",
        required=True
    )
    args = parser.parse_args()
    steam_cmd = args.steam_cmd
    steam_account_name = args.steam_account_name

    BASE_FOLDER = "local"
    cwd = os.getcwd()

    # Iterate through sub-folders and upload items
    for folder_name in os.listdir(BASE_FOLDER):
        print(f"Processing: {folder_name}")
        map_name = folder_name

        map_path = os.path.join(cwd, BASE_FOLDER, map_name)
        preview_file = os.path.join(cwd, "assets", "thumbnails",
                                    f"{map_name}.PNG")

        # Check if required files exist
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Content folder missing: {map_path}")
        if not os.path.exists(preview_file):
            raise FileNotFoundError(f"Preview file missing: {preview_file}")

        # Check if the folder name has a corresponding published_file_id
        if map_name not in published_file_id_map:
            raise KeyError(f"No published_file_id found for {map_name}.")

        # Generate metadata for the VDF
        title = f"zitrez {map_name} annotations"
        URL = "https://github.com/ReneRebsdorf/CS2-annotations"
        description = f"Map annotations from {URL}"
        published_file_id = published_file_id_map[map_name]

        # Create a temporary VDF file for this folder
        temp_vdf = os.path.join(map_path, "metadata.vdf")
        generate_vdf(
            temp_vdf, map_path, preview_file, title,
            description, published_file_id
        )

        # Run SteamCMD to upload the item
        subprocess.run([  # nosec - This is a trusted command
            steam_cmd,
            "+login",
            steam_account_name,
            "+workshop_build_item", temp_vdf,
            "+quit"
        ], check=True)
        print(f"Successfully uploaded: {map_name}.")

        # Clean up temporary VDF file
        os.remove(temp_vdf)

        print(f"Finished processing: {map_name}")

    print("All items processed.")
