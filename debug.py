# [file name]: debug_files.py
"""
Enhanced debug script to test file loading
"""
import os
import logging
from file_manager import FileManager

# Setup logging to see all messages
logging.basicConfig(level=logging.INFO)

def test_file_loading():
    """Test loading specific files"""
    print("🧪 Testing file loading...")
    
    # Test cases - adjust these based on your actual files
    test_cases = [
        {
            'year': 'year_1',
            'term': 'term_1', 
            'block': 'block_1',
            'subject': 'anatomy',
            'category': 'general',
            'subtopic': '01_Introduction to Anatomy.csv'
        },
        {
            'year': 'year_1',
            'term': 'term_1',
            'block': 'block_1', 
            'subject': 'anatomy',
            'category': 'midterm',
            'subtopic': '01_Midterm Questions.csv'
        },
        {
            'year': 'year_1',
            'term': 'term_1',
            'block': 'block_1',
            'subject': 'histology', 
            'category': 'general',
            'subtopic': '01_Paraffin technique.csv'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['subtopic']}")
        questions = FileManager.load_questions(
            test_case['year'],
            test_case['term'], 
            test_case['block'],
            test_case['subject'],
            test_case['category'],
            test_case['subtopic']
        )
        
        if questions:
            print(f"✅ SUCCESS: Loaded {len(questions)} questions")
            # Show first question as sample
            if questions:
                first_q = questions[0]
                print(f"   Sample: {first_q['question'][:50]}...")
                print(f"   Options: {[opt[:20] + '...' for opt in first_q['options']]}")
                print(f"   Correct: {first_q['correct_index']}")
        else:
            print(f"❌ FAILED: No questions loaded")

def list_all_navigation():
    """List all available navigation paths"""
    print("\n🗺️ Navigation Structure:")
    
    years = FileManager.list_years()
    print(f"Years: {years}")
    
    for year in years:
        terms = FileManager.list_terms(year)
        print(f"  {year}: {terms}")
        
        for term in terms:
            blocks = FileManager.list_blocks(year, term)
            print(f"    {term}: {blocks}")
            
            for block in blocks:
                subjects = FileManager.list_subjects(year, term, block)
                print(f"      {block}: {subjects}")
                
                for subject in subjects:
                    categories = FileManager.list_categories(year, term, block, subject)
                    print(f"        {subject}: {categories}")
                    
                    for category in categories:
                        subtopics = FileManager.list_subtopics(year, term, block, subject, category)
                        print(f"          {category}: {len(subtopics)} subtopics")
                        for subtopic in subtopics[:3]:  # Show first 3
                            print(f"            - {subtopic}")

if __name__ == "__main__":
    test_file_loading()
    list_all_navigation()