#!/usr/bin/env python3
"""
Comprehensive debug for file discovery
"""
import os
from config import CONFIG, NAVIGATION_STRUCTURE
from file_manager import FileManager

def debug_file_discovery():
    print("🔍 COMPREHENSIVE FILE DISCOVERY DEBUG")
    print("=" * 60)
    
    # Check base directory
    base_path = CONFIG["data_dir"]
    print(f"📁 Base data directory: {base_path}")
    print(f"   Exists: {os.path.exists(base_path)}")
    
    if not os.path.exists(base_path):
        print("❌ Data directory does not exist!")
        return
    
    # Check year_1
    year_path = os.path.join(base_path, "year_1")
    print(f"\n📅 Year 1 path: {year_path}")
    print(f"   Exists: {os.path.exists(year_path)}")
    
    if os.path.exists(year_path):
        print(f"   Contents: {os.listdir(year_path)}")
        
        # Check term_1
        term_path = os.path.join(year_path, "term_1")
        print(f"\n   📚 Term 1 path: {term_path}")
        print(f"      Exists: {os.path.exists(term_path)}")
        
        if os.path.exists(term_path):
            print(f"      Contents: {os.listdir(term_path)}")
            
            # Check block_1
            block_path = os.path.join(term_path, "block_1")
            print(f"\n      🧩 Block 1 path: {block_path}")
            print(f"         Exists: {os.path.exists(block_path)}")
            
            if os.path.exists(block_path):
                print(f"         Contents: {os.listdir(block_path)}")
                
                # Check anatomy
                anatomy_path = os.path.join(block_path, "anatomy")
                print(f"\n         📊 Anatomy path: {anatomy_path}")
                print(f"            Exists: {os.path.exists(anatomy_path)}")
                
                if os.path.exists(anatomy_path):
                    print(f"            Contents: {os.listdir(anatomy_path)}")
                    
                    # Check general category
                    general_path = os.path.join(anatomy_path, "general")
                    print(f"\n            📂 General path: {general_path}")
                    print(f"               Exists: {os.path.exists(general_path)}")
                    
                    if os.path.exists(general_path):
                        csv_files = [f for f in os.listdir(general_path) if f.endswith('.csv')]
                        print(f"               CSV files: {csv_files}")
                        
                        # Look for the specific file
                        target_file = "24_Derivatives of the Ectodermal Germ Layer.csv"
                        print(f"\n            🔎 Looking for: {target_file}")
                        print(f"               Exists: {os.path.exists(os.path.join(general_path, target_file))}")
                        
                        if os.path.exists(os.path.join(general_path, target_file)):
                            print("✅ FILE FOUND!")
                        else:
                            print("❌ FILE NOT FOUND!")
                            print("   Available files:")
                            for file in csv_files:
                                print(f"   - {file}")

def debug_navigation_structure():
    print("\n\n🔍 NAVIGATION STRUCTURE DEBUG")
    print("=" * 60)
    
    print("Available years:", FileManager.list_years())
    
    for year in FileManager.list_years():
        print(f"\n📅 {year}: {FileManager.get_year_display_name(year)}")
        print("   Terms:", FileManager.list_terms(year))
        
        for term in FileManager.list_terms(year):
            print(f"   📚 {term}: {FileManager.get_term_display_name(year, term)}")
            print("      Blocks:", FileManager.list_blocks(year, term))
            
            for block in FileManager.list_blocks(year, term):
                print(f"      🧩 {block}: {FileManager.get_block_display_name(year, term, block)}")
                print("         Subjects:", FileManager.list_subjects(year, term, block))
                
                for subject in FileManager.list_subjects(year, term, block):
                    print(f"         📊 {subject}: {FileManager.get_subject_display_name(year, term, block, subject)}")
                    print("            Categories:", FileManager.list_categories(year, term, block, subject))
                    
                    for category in FileManager.list_categories(year, term, block, subject):
                        print(f"            📂 {category}: {FileManager.get_category_display_name(year, term, block, subject, category)}")
                        subtopics = FileManager.list_subtopics(year, term, block, subject, category)
                        print("               Subtopics:", len(subtopics))
                        
                        for subtopic in subtopics[:5]:  # Show first 5
                            display_name = FileManager.get_subtopic_display_name(year, term, block, subject, category, subtopic)
                            print(f"               - {subtopic} → '{display_name}'")

def debug_specific_file():
    print("\n\n🔍 SPECIFIC FILE DEBUG")
    print("=" * 60)
    
    # Test loading the specific file that's failing
    year = "year_1"
    term = "term_1" 
    block = "block_1"
    subject = "anatomy"
    category = "general"
    
    subtopics = FileManager.list_subtopics(year, term, block, subject, category)
    print(f"Subtopics in {year}/{term}/{block}/{subject}/{category}:")
    for i, subtopic in enumerate(subtopics, 1):
        display_name = FileManager.get_subtopic_display_name(year, term, block, subject, category, subtopic)
        print(f"  {i}. {subtopic} → '{display_name}'")
    
    # Look for files containing "Ectodermal"
    ectodermal_files = [f for f in subtopics if "Ectodermal" in f or "ectodermal" in f.lower()]
    print(f"\nFiles containing 'Ectodermal': {ectodermal_files}")

if __name__ == "__main__":
    debug_file_discovery()
    debug_navigation_structure() 
    debug_specific_file()