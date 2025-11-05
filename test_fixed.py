# [file name]: test_fixed.py
"""
Test the fixed automated navigation system
"""
from init_navigation import initialize_navigation, NAVIGATION_STRUCTURE
from file_manager import FileManager

def test_fixed_system():
    print("🧪 Testing Fixed Automated Navigation System")
    print("=" * 50)
    
    # Initialize navigation
    if initialize_navigation():
        print("✅ Navigation initialized successfully!")
        
        # Test listing content
        years = FileManager.list_years()
        print(f"📚 Years found: {years}")
        
        if years:
            for year in years:
                print(f"\n📅 {FileManager.get_year_display_name(year)}")
                subjects = FileManager.list_subjects(year, "term_1", "block_1")
                
                for subject in subjects:
                    print(f"  📖 {FileManager.get_subject_display_name(year, 'term_1', 'block_1', subject)}")
                    categories = FileManager.list_categories(year, "term_1", "block_1", subject)
                    
                    for category in categories:
                        print(f"    🗂️ {FileManager.get_category_display_name(year, 'term_1', 'block_1', subject, category)}")
                        subtopics = FileManager.list_subtopics(year, "term_1", "block_1", subject, category)
                        print(f"      📄 {len(subtopics)} quiz files")
    else:
        print("❌ Navigation initialization failed!")

if __name__ == "__main__":
    test_fixed_system()
