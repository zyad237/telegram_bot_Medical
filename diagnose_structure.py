# find_structure.py
import os

def find_actual_paths():
    base_dir = "data"
    print("🔍 Scanning directory structure...")
    
    for root, dirs, files in os.walk(base_dir):
        level = root.replace(base_dir, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        
        subindent = '  ' * (level + 1)
        for file in files:
            if file.endswith('.csv'):
                print(f"{subindent}📄 {file}")

if __name__ == "__main__":
    find_actual_paths()