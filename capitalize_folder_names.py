from sys import argv
import os


path = os.getcwd()
if (len(argv) >= 2):
    path = argv[1]

print('Searching for folders in ' + path)

# Go through all folders and capitalize the folder names
dirsList = []
for root, dirs, _ in os.walk(path):
    for dir in dirs:
        changedDirName = dir.capitalize().replace(' ', '_')
        if (changedDirName != dir):
            dirsList.append((root, dir, changedDirName))

print(f"Found {len(dirsList)} folders where name shall be capitalized.")

for (root, dir, changedDirName) in reversed(dirsList):
    print(f"Renaming folder {dir} to {changedDirName} ...")
    old_dir_name = os.path.join(root, dir)
    new_dir_name = os.path.join(root, changedDirName)
    os.rename(old_dir_name, new_dir_name)

print('Complete.')
