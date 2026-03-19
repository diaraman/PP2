import os
import shutil

source="sample.txt"
backup="backup_sample.txt"
shutil.copy2(source, backup)
print("Backup created")
if os.path.exists(backup):
    print("Backup exists")
    os.remove(backup)
    print("Backup file deleted")
else:
    print("Backup file doesn't exist")