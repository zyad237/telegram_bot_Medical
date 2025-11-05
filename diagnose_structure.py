# check_structure.py
import os
from config import CONFIG, NAVIGATION_STRUCTURE

print("NAVIGATION_STRUCTURE:", NAVIGATION_STRUCTURE)
print("Is empty?", not bool(NAVIGATION_STRUCTURE))

data_dir = CONFIG["data_dir"]
print("Data dir exists:", os.path.exists(data_dir))

if os.path.exists(data_dir):
    print("Contents:", os.listdir(data_dir))