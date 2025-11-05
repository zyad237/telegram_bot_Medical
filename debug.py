#!/usr/bin/env python3
"""
Debug script to check file structure and CSV files
"""
import os
from file_manager import FileManager

def debug_file_structure():
    print("🔍 Debugging File Structure...")
    
    # Check data directory
    data_dir = FileManager.get_data_path()
    print(f"📁 Data directory: {data_dir}")
    print(f"📁 Data directory exists: {os.path.exists(data_dir)}")
    
    if os.path.exists(data_dir):
        print("📂 Contents of data directory:")
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                # List subdirectories
                for subitem in os.listdir(item_path):
                    subitem_path = os.path.join(item_path, subitem)
                    if os.path.isdir(subitem_path):
                        print(f"    📁 {subitem}/")
                    else:
                        print(f"    📄 {subitem}")
            else:
                print(f"  📄 {item}")
    
    # List all CSV files recursively
    print("\n🔍 All CSV files found:")
    csv_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.csv'):
                full_path = os.path.join(root, file)
                csv_files.append(full_path)
                print(f"  📄 {file} -> {full_path}")
    
    print(f"\n📊 Total CSV files found: {len(csv_files)}")
    
    # Test loading a specific file
    if csv_files:
        test_file = csv_files[0]
        print(f"\n🧪 Testing load_questions with: {os.path.basename(test_file)}")
        
        # Extract filename for testing
        filename = os.path.basename(test_file)
        questions = FileManager.load_questions("year_1", "term_1", "block_1", "anatomy", "general", filename)
        print(f"✅ Loaded {len(questions)} questions from test file")

if __name__ == "__main__":
    debug_file_structure()