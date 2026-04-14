import pathlib

# Define the path (using expanduser to handle the ~)
path_str = "~/Apps/FinalNBA/data/raw/2020-21/playbyplay/"
folder_path = pathlib.Path(path_str).expanduser()

if folder_path.exists() and folder_path.is_dir():
    # This creates a list of all files and gets the length
    file_count = len([f for f in folder_path.iterdir() if f.is_file()])
    print(f"Total files in {folder_path.name}: {file_count}")
else:
    print("Error: The directory does not exist. Check your path spelling!")