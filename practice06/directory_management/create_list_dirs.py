import os

base = "workspace"
source_docs = os.path.join(base, "source", "docs")
destination = os.path.join(base, "destination")

# 1) To create nested folders
os.makedirs(source_docs, exist_ok=True)
os.makedirs(destination, exist_ok=True)

# 2) To show folders in workspace
print("Folders in workspace:")
print(os.listdir(base))

# 3) To show everything(directory tree)
print("\nDirectory tree:")
for root, dirs, files in os.walk(base):
    print(f"Root: {root}")
    print(f"  Dirs: {dirs}")
    print(f"  Files: {files}")
