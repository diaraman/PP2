import os
import shutil

source = "workspace/source"
destination = "workspace/destination"

# 1) creating folders
os.makedirs(source, exist_ok=True)
os.makedirs(destination, exist_ok=True)

# 2) creating files in Source 
with open(os.path.join(source, "a.txt"), "w", encoding="utf-8") as f:
    f.write("This is A file")

with open(os.path.join(source, "b.txt"), "w", encoding="utf-8") as f:
    f.write("This is B file")

# 3) a.txt -> copy (Copy from source and paste to destination)
shutil.copy(
    os.path.join(source, "a.txt"),
    os.path.join(destination, "a.txt")
)

# 4) b.txt -> move (move from Source to Destination)
shutil.move(
    os.path.join(source, "b.txt"),
    os.path.join(destination, "b.txt")
)

# 5) to show results
print("files in Source:", os.listdir(source))
print("Files in Destination:", os.listdir(destination))
