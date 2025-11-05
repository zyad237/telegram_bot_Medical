# [file name]: debug_navigation.py
"""
Debug script to check navigation structure and CSV file population
"""
import os
from config import CONFIG, NAVIGATION_STRUCTURE

def debug_navigation():
    print("🔍 DEBUGGING NAVIGATION STRUCTURE")
    print("=" * 60)
    
    # Check the exact navigation path for midterm
    year = "year_1"
    term = "term_1"
    block = "block_1"
    subject = "anatomy"
    category = "midterm"
    
    print(f"📍 Checking navigation path: {year}/{term}/{block}/{subject}/{category}")
    
    # Navigate through the structure
    try:
        year_data = NAVIGATION_STRUCTURE.get(year)
        print(f"📅 Year found: {year_data is not None}")
        
        if year_data:
            term_data = year_data["terms"].get(term)
            print(f"📚 Term found: {term_data is not None}")
            
            if term_data:
                block_data = term_data["blocks"].get(block)
                print(f"📦 Block found: {block_data is not None}")
                
                if block_data:
                    subject_data = block_data["subjects"].get(subject)
                    print(f"📊 Subject found: {subject_data is not None}")
                    
                    if subject_data:
                        category_data = subject_data["categories"].get(category)
                        print(f"📝 Category found: {category_data is not None}")
                        
                        if category_data:
                            print(f"📄 Subtopic keys: {list(category_data['subtopics'].keys())}")
                            print(f"📄 Subtopic values: {category_data['subtopics']}")
                        else:
                            print("❌ Category data not found in navigation structure")
                    else:
                        print("❌ Subject data not found in navigation structure")
                else:
                    print("❌ Block data not found in navigation structure")
            else:
                print("❌ Term data not found in navigation structure")
        else:
            print("❌ Year data not found in navigation structure")
    
    except Exception as e:
        print(f"❌ Error navigating structure: {e}")
    
    print("\n" + "=" * 60)
    print("📁 CHECKING ACTUAL FILES ON DISK")
    
    # Check actual files on disk
    category_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
    print(f"📁 Disk path: {category_path}")
    print(f"📁 Path exists: {os.path.exists(category_path)}")
    
    if os.path.exists(category_path):
        files = os.listdir(category_path)
        csv_files = [f for f in files if f.endswith('.csv')]
        print(f"📄 All files: {files}")
        print(f"📄 CSV files: {csv_files}")
        
        if csv_files:
            print(f"\n📖 Sample CSV content:")
            sample_file = os.path.join(category_path, csv_files[0])
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]  # First 3 lines
                    for i, line in enumerate(lines):
                        print(f"  Line {i+1}: {line.strip()}")
            except Exception as e:
                print(f"  ❌ Error reading file: {e}")
        else:
            print("❌ No CSV files found on disk!")
    else:
        print("❌ Category directory does not exist!")

if __name__ == "__main__":
    debug_navigation()