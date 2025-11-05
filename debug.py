# [file name]: check_structure.py
"""
Diagnostic script to check the actual file structure
"""
import os

def check_directory_structure(base_dir="data"):
    """Check what directories and files actually exist"""
    print("🔍 Checking directory structure...")
    
    if not os.path.exists(base_dir):
        print(f"❌ Data directory '{base_dir}' does not exist!")
        return
    
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.csv'):
                print(f"{subindent}📄 {file}")

if __name__ == "__main__":
    check_directory_structure()