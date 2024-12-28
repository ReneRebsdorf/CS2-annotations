import os
import subprocess  # nosec - This is a trusted command

# TODO: Ensure sub-process calls throw exceptions on error
# TODO: Write tests
# TODO: Update github runner to run this script

# Define variables
base_folder = "local"
steamcmd_path = "C:\\path\\to\\steamcmd.exe"  # TODO: Update this

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


# Function to check and download SteamCMD if necessary
def check_and_download_steamcmd():
    if not os.path.exists(steamcmd_path):
        domain = "steamcdn-a.akamaihd.net"
        url = f"https://{domain}/client/installer/steamcmd_linux.tar.gz"
        print(f"SteamCMD not found. Downloading from {url}...")

        subprocess.run(  # nosec - This is a trusted command
            ["curl", "-sqL", url],
            stdout=subprocess.PIPE, check=True
        )
        subprocess.run(  # nosec - This is a trusted command
            ["tar", "zxvf", "-"],
            stdout=subprocess.PIPE, check=True
        )
        print("SteamCMD downloaded successfully.")


# Function to generate the VDF content
def generate_vdf(output_path, content_folder, preview_file, title,
                 description, published_file_id):
    vdf_content = f"""
    "workshopitem"
    {{
        "appid"            "730"
        "contentfolder"    "{content_folder}"
        "previewfile"      "{preview_file}"
        "visibility"       "0"
        "title"            "{title}"
        "description"      "{description}"
        "publishedfileid"  "{published_file_id}"
    }}
    """

    with open(output_path, "w") as output:
        output.write(vdf_content)


# Check and download SteamCMD if necessary
check_and_download_steamcmd()

# Iterate through sub-folders and upload items
for folder_name in os.listdir(base_folder):
    folder_path = os.path.join(base_folder, folder_name)

    if os.path.isdir(folder_path):
        # file name is the same as the folder name with .txt
        file_name = folder_name + ".txt"
        content_file = os.path.join(folder_path, file_name)
        preview_file = os.path.join("assets", folder_name, ".PNG")

        # Check if required files exist
        if not os.path.exists(content_file):
            raise FileNotFoundError(f"Content file missing for {folder_name}.")
        if not os.path.exists(preview_file):
            raise FileNotFoundError(f"Preview file missing for {folder_name}.")

        # Check if the folder name has a corresponding published_file_id
        if folder_name not in published_file_id_map:
            raise KeyError(f"No published_file_id found for {folder_name}.")

        # Generate metadata for the VDF
        title = f"zitrez {folder_name} annotations"
        url = "https://github.com/ReneRebsdorf/CS2-annotations"
        description = f"Map annotations from {url}"
        published_file_id = published_file_id_map[folder_name]

        # Create a temporary VDF file for this folder
        temp_vdf = os.path.join(folder_path, f"{folder_name}_metadata.vdf")
        generate_vdf(
            temp_vdf, folder_path, preview_file, title,
            description, published_file_id
        )

        # Run SteamCMD to upload the item
        subprocess.run([  # nosec - This is a trusted command
            # TODO: Determine if steam guard can be prompted,
            #       which then requires user input which is probably fine
            #       otherwise, I will probably need to make a new account
            #       for this purpose
            steamcmd_path,
            "+login",
            "<username>",  # TODO: Replace with env var
            "<password>",  # TODO: Replace with env var
            "+workshop_build_item", temp_vdf,
            "+quit"
        ], check=True)
        print(f"Successfully uploaded {folder_name}.")

        # Clean up temporary VDF file
        os.remove(temp_vdf)

print("All items processed.")
