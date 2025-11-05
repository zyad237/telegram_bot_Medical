# [file name]: test_auto_nav.py
"""
Test the automated navigation system
"""
from auto_navigator import AutoNavigator
from file_manager import FileManager

def test_automated_system():
    print("🧪 Testing Automated Navigation System")
    print("=" * 50)
    
    # Build structure
    structure = AutoNavigator.build_navigation_structure()
    
    if not structure:
        print("❌ No structure built! Check your data directory.")
        return
    
    print("✅ Navigation Structure Built Successfully!")
    print("\n📋 Available Content:")
    
    # Test listing all available content
    years = FileManager.list_years()
    print(f"Years: {years}")
    
    for year in years:
        print(f"\n📅 {FileManager.get_year_display_name(year)}")
        subjects = FileManager.list_subjects(year, "term_1", "block_1")
        
        for subject in subjects:
            print(f"  📖 {FileManager.get_subject_display_name(year, 'term_1', 'block_1', subject)}")
            categories = FileManager.list_categories(year, "term_1", "block_1", subject)
            
            for category in categories:
                print(f"    🗂️ {FileManager.get_category_display_name(year, 'term_1', 'block_1', subject, category)}")
                subtopics = FileManager.list_subtopics(year, "term_1", "block_1", subject, category)
                
                for subtopic in subtopics[:3]:  # Show first 3
                    display_name = FileManager.get_subtopic_display_name(year, "term_1", "block_1", subject, category, subtopic)
                    print(f"      📄 {display_name}")
                
                if len(subtopics) > 3:
                    print(f"      ... and {len(subtopics) - 3} more")
    
    # Test loading a file
    print("\n🔍 Testing File Loading...")
    if years and subjects:
        test_year = years[0]
        test_subject = subjects[0]
        test_categories = FileManager.list_categories(test_year, "term_1", "block_1", test_subject)
        
        if test_categories:
            test_category = test_categories[0]
            test_subtopics = FileManager.list_subtopics(test_year, "term_1", "block_1", test_subject, test_category)
            
            if test_subtopics:
                test_subtopic = test_subtopics[0]
                print(f"Testing: {test_year}/{test_subject}/{test_category}/{test_subtopic}")
                
                questions = FileManager.load_questions(
                    test_year, "term_1", "block_1", test_subject, test_category, test_subtopic
                )
                
                if questions:
                    print(f"✅ SUCCESS: Loaded {len(questions)} questions")
                    print(f"Sample: {questions[0]['question'][:50]}...")
                else:
                    print("❌ FAILED: No questions loaded")

if __name__ == "__main__":
    test_automated_system()