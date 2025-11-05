#!/usr/bin/env python3
"""
Comprehensive fix for directory and file structure issues
"""
import os
import shutil
from config import NAVIGATION_STRUCTURE, CONFIG

def comprehensive_diagnosis():
    print("🔍 COMPREHENSIVE STRUCTURE DIAGNOSIS")
    print("=" * 70)
    
    year = "year_1"
    term = "term_1" 
    block = "block_1"
    subject = "anatomy"
    
    base_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
    
    print(f"📁 Base path: {base_path}")
    print()
    
    if not os.path.exists(base_path):
        print(f"❌ Base path doesn't exist: {base_path}")
        return
    
    # Check each category
    categories = ["general", "Midterm", "Final", "Formative"]
    
    for category in categories:
        category_path = os.path.join(base_path, category)
        print(f"\n📂 Checking: {category}")
        print(f"   Path: {category_path}")
        
        # Check if directory exists
        if not os.path.exists(category_path):
            print(f"   ❌ DIRECTORY MISSING")
            continue
        
        # Check what CSV files exist
        csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')] if os.path.exists(category_path) else []
        print(f"   📄 Found {len(csv_files)} CSV files: {csv_files}")
        
        # Check what files are expected from config
        expected_files = []
        if (year in NAVIGATION_STRUCTURE and 
            "terms" in NAVIGATION_STRUCTURE[year] and
            term in NAVIGATION_STRUCTURE[year]["terms"] and
            "blocks" in NAVIGATION_STRUCTURE[year]["terms"][term] and
            block in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"] and
            "subjects" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block] and
            subject in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"] and
            "categories" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject] and
            category in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"]):
            
            expected_files = list(NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"].keys())
        
        print(f"   📋 Expected files from config: {expected_files}")
        
        # Check for mismatches
        missing_files = set(expected_files) - set(csv_files)
        extra_files = set(csv_files) - set(expected_files)
        
        if missing_files:
            print(f"   ❌ MISSING FILES: {list(missing_files)}")
        if extra_files:
            print(f"   ⚠️  EXTRA FILES (not in config): {list(extra_files)}")
        
        if not missing_files and not extra_files:
            print(f"   ✅ Perfect match!")

def create_missing_files():
    print("\n" + "=" * 70)
    print("🛠️  CREATING MISSING FILES AND DIRECTORIES")
    print("=" * 70)
    
    year = "year_1"
    term = "term_1"
    block = "block_1" 
    subject = "anatomy"
    
    base_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
    
    # Ensure base path exists
    os.makedirs(base_path, exist_ok=True)
    
    categories = ["general", "Midterm", "Final", "Formative"]
    
    for category in categories:
        category_path = os.path.join(base_path, category)
        
        # Create category directory
        os.makedirs(category_path, exist_ok=True)
        print(f"\n📁 Ensuring directory: {category_path}")
        
        # Get expected files from config
        expected_files = []
        if (year in NAVIGATION_STRUCTURE and 
            "terms" in NAVIGATION_STRUCTURE[year] and
            term in NAVIGATION_STRUCTURE[year]["terms"] and
            "blocks" in NAVIGATION_STRUCTURE[year]["terms"][term] and
            block in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"] and
            "subjects" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block] and
            subject in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"] and
            "categories" in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject] and
            category in NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"]):
            
            expected_files = list(NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"][category]["subtopics"].keys())
        
        # Create empty CSV files for missing ones
        for expected_file in expected_files:
            file_path = os.path.join(category_path, expected_file)
            if not os.path.exists(file_path):
                # Create empty CSV with headers
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Question,Option A,Option B,Option C,Option D,Correct Answer\n")
                    f.write("Sample question,Choice A,Choice B,Choice C,Choice D,A\n")
                print(f"   ✅ Created: {expected_file}")
            else:
                print(f"   📄 Already exists: {expected_file}")

def copy_files_from_general():
    """Copy files from general to other categories as templates"""
    print("\n" + "=" * 70)
    print("📋 COPYING TEMPLATE FILES FROM GENERAL CATEGORY")
    print("=" * 70)
    
    year = "year_1"
    term = "term_1"
    block = "block_1" 
    subject = "anatomy"
    
    base_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
    general_path = os.path.join(base_path, "general")
    
    if not os.path.exists(general_path):
        print("❌ General directory doesn't exist - cannot copy templates")
        return
    
    # Get CSV files from general
    general_files = [f for f in os.listdir(general_path) if f.endswith('.csv')]
    
    if not general_files:
        print("❌ No CSV files in general directory")
        return
    
    print(f"📄 Found {len(general_files)} files in general directory")
    
    # Copy to other categories
    other_categories = ["Midterm", "Final", "Formative"]
    
    for category in other_categories:
        category_path = os.path.join(base_path, category)
        os.makedirs(category_path, exist_ok=True)
        
        print(f"\n📁 Copying to {category}:")
        
        # Copy first 3 files from general as templates
        for i, source_file in enumerate(general_files[:3]):
            # Create new filename for this category
            if category == "Midterm":
                new_filename = f"{i+1:02d}_Midterm Questions.csv"
            elif category == "Final":
                new_filename = f"{i+1:02d}_Final Questions.csv"  
            elif category == "Formative":
                new_filename = f"{i+1:02d}_Formative.csv"
            
            source_path = os.path.join(general_path, source_file)
            dest_path = os.path.join(category_path, new_filename)
            
            if not os.path.exists(dest_path):
                shutil.copy2(source_path, dest_path)
                print(f"   ✅ Copied: {source_file} → {new_filename}")
            else:
                print(f"   📄 Already exists: {new_filename}")

if __name__ == "__main__":
    comprehensive_diagnosis()
    create_missing_files()
    copy_files_from_general()
    print("\n🎉 Setup complete! Check the structure above.")