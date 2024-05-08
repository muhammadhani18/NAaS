import os
import glob
import pathlib
# # Define the directory path
# directory = "../Scrapper/2024"

# # Iterate over all directories inside the '2024' directory
# for subdir in os.listdir(directory):
#     # Check if the current item is a directory
#     if os.path.isdir(os.path.join(directory, subdir)):
#         # Iterate over files in the current directory
#         print(f"Files in {subdir}:")
#         subdir_path = os.path.join(directory, subdir)
#         for filename in os.listdir(subdir_path):
#             # Check if the current item is a file
#             if os.path.isfile(os.path.join(subdir_path, filename)):
#                 print(filename)
count = 0
for filename in glob.iglob(r'../Scrapper/2024/**/*.csv', recursive=True):
    path = pathlib.PurePath(filename)
    fileName = path.name[:-4]
    print(fileName)
    count +=1

print(count)