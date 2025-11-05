# [file name]: debug_midterm.py
"""
Debug script to check why midterm files aren't being found
"""
import os
from config import CONFIG, NAVIGATION_STRUCTURE
from file_manager import FileManager

def debug_midterm_files():
    print("🔍 Debugging Midterm File Access")
    print("=" * 50)
    
    # Test specific path that's failing
    year = "year_1"
    term = "term_1"
    block = "block_1"
    subject = "anatomy"
    category = "midterm"
    
    print(f"Testing path: {year}/{term}/{block}/{subject}/{category}")
    
    # Check if directory exists
    expected_path = os.path.join(CONFIG["data_dir"], year, term, block, subject, category)
    print(f"Expected path: {expected_path}")
    print(f"Directory exists: {os.path.exists(expected_path)}")
    
    if os.path.exists(expected_path):
        print("\n📁 Contents of directory:")
        files = os.listdir(expected_path)
        for file in files:
            file_type = "📄 CSV" if file.endswith('.csv') else "📁 Dir"
            print(f"  {file_type}: {file}")
    
    # Test FileManager methods
    print(f"\n🧪 Testing FileManager methods:")
    print(f"List years: {FileManager.list_years()}")
    print(f"List terms: {FileManager.list_terms(year)}")
    print(f"List blocks: {FileManager.list_blocks(year, term)}")
    print(f"List subjects: {FileManager.list_subjects(year, term, block)}")
    print(f"List categories: {FileManager.list_categories(year, term, block, subject)}")
    print(f"List subtopics: {FileManager.list_subtopics(year, term, block, subject, category)}")
    
    # Check navigation structure
    print(f"\n📋 Navigation structure check:")
    path = FileManager.get_navigation_path(year, term, block, subject, category)
    if path and "subtopics" in path:
        print(f"Subtopics in navigation: {list(path['subtopics'].keys())}")
    else:
        print("❌ No subtopics found in navigation structure")
    
    # Test loading a specific file
    print(f"\n🧪 Testing file loading:")
    subtopics = FileManager.list_subtopics(year, term, block, subject, category)
    if subtopics:
        test_file = subtopics[0]
        print(f"Testing file: {test_file}")
        questions = FileManager.load_questions(year, term, block, subject, category, test_file)
        print(f"Questions loaded: {len(questions)}")
    else:
        print("❌ No subtopics to test")

def check_all_csv_locations():
    """Check all possible locations where CSV files might be"""
    print(f"\n🔎 Searching for CSV files in entire data directory...")
    
    csv_files = []
    for root, dirs, files in os.walk(CONFIG["data_dir"]):
        for file in files:
            if file.endswith('.csv'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, CONFIG["data_dir"])
                csv_files.append((rel_path, file))
    
    print(f"Found {len(csv_files)} CSV files:")
    for path, file in csv_files:
        print(f"  📄 {path}")

if __name__ == "__main__":
    debug_midterm_files()
    check_all_csv_locations()