import os

# Define the main path
main_path = r"E:\五大任务数据集\疲劳检测"

# Get the list of the five main folders
main_folders = [f for f in os.listdir(main_path) if os.path.isdir(os.path.join(main_path, f))]

# Ensure we have folders to process
if not main_folders:
    print("No folders found in the specified path.")
else:
    # Iterate through each main folder
    for folder in sorted(main_folders):
        folder_path = os.path.join(main_path, folder)
        # Get subfolders (video numbers)
        subfolders = [sf for sf in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, sf))]

        # Print the results for the current folder
        print(f"\nVideo numbers in folder '{folder}':")
        if subfolders:
            for subfolder in sorted(subfolders):
                print(subfolder)
        else:
            print("No subfolders found.")