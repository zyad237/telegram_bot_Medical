# [file name]: check_midterm_files.py
"""
Diagnostic script to check midterm file access
"""
import os
from config import CONFIG

def check_midterm_files():
    print("🔍 Checking Midterm Files")
    print("=" * 50)
    
    # Test the exact path that's failing
    test_path = os.path.join(CONFIG["data_dir"], "year_1", "term_1", "block_1", "anatomy", "midterm")
    print(f"📁 Checking path: {test_path}")
    print(f"Path exists: {os.path.exists(test_path)}")
    
    if os.path.exists(test_path):
        print(f"\n📄 Files in midterm directory:")
        files = os.listdir(test_path)
        for file in files:
            file_path = os.path.join(test_path, file)
            file_type = "📄 CSV" if file.endswith('.csv') else "📁 Directory"
            print(f"  {file_type}: {file}")
            
            if file.endswith('.csv'):
                # Test if file can be read
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        print(f"    Sample: {first_line[:50]}...")
                except Exception as e:
                    print(f"    ❌ Error reading: {e}")
    else:
        print(f"❌ Directory does not exist: {test_path}")
        
        # Show what directories actually exist
        print(f"\n🔍 Exploring directory structure:")
        base_path = os.path.join(CONFIG["data_dir"], "year_1", "term_1", "block_1", "anatomy")
        if os.path.exists(base_path):
            subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            print(f"Subdirectories in anatomy: {subdirs}")
        else:
            print(f"Base path doesn't exist: {base_path}")

if __name__ == "__main__":
    check_midterm_files()