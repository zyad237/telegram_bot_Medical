# [file name]: check_directory_structure.py
"""
Check the actual directory structure
"""
import os
from config import CONFIG

def check_directory_structure():
    print("🔍 CHECKING DIRECTORY STRUCTURE")
    print("=" * 50)
    
    data_dir = CONFIG["data_dir"]
    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Exists: {os.path.exists(data_dir)}")
    
    if not os.path.exists(data_dir):
        print("❌ Data directory doesn't exist!")
        return
    
    print("\n📂 Contents of data directory:")
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        item_type = "📁 DIR" if os.path.isdir(item_path) else "📄 FILE"
        print(f"  {item_type}: {item}")
        
        # If it's a directory, show its contents
        if os.path.isdir(item_path):
            for subitem in os.listdir(item_path):
                subitem_path = os.path.join(item_path, subitem)
                subitem_type = "📁 DIR" if os.path.isdir(subitem_path) else "📄 FILE"
                print(f"    {subitem_type}: {subitem}")

def check_specific_path():
    print("\n" + "=" * 50)
    print("🔍 CHECKING SPECIFIC MIDTERM PATH")
    
    test_path = os.path.join("data", "year_1", "term_1", "block_1", "anatomy", "midterm")
    print(f"📁 Testing path: {test_path}")
    print(f"📁 Exists: {os.path.exists(test_path)}")
    
    if os.path.exists(test_path):
        print("📄 Files in midterm directory:")
        for file in os.listdir(test_path):
            print(f"  📄 {file}")

if __name__ == "__main__":
    check_directory_structure()
    check_specific_path()