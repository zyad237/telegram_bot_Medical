#!/usr/bin/env python3
"""
Diagnostic script to check directory structure
"""
import os
from config import NAVIGATION_STRUCTURE, CONFIG

def diagnose_structure():
    print("🔍 DIAGNOSING DIRECTORY STRUCTURE")
    print("=" * 60)
    
    # Check Year 1 structure
    year = "year_1"
    term = "term_1" 
    block = "block_1"
    subject = "anatomy"
    
    base_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
    
    print(f"📁 Checking path: {base_path}")
    print()
    
    if not os.path.exists(base_path):
        print(f"❌ Base path doesn't exist: {base_path}")
        return
    
    # Check what categories actually exist
    actual_categories = [d for d in os.listdir(base_path) 
                        if os.path.isdir(os.path.join(base_path, d))]
    
    print(f"📂 ACTUAL directories in anatomy:")
    for category in actual_categories:
        category_path = os.path.join(base_path, category)
        csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
        print(f"  📂 {category}: {len(csv_files)} CSV files")
        for csv_file in csv_files:
            print(f"    📄 {csv_file}")
    
    print()
    print(f"📋 EXPECTED categories from config:")
    expected_categories = list(NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].keys())
    for category in expected_categories:
        print(f"  📋 {category}")
    
    print()
    print("🔍 COMPARISON:")
    missing_dirs = set(expected_categories) - set(actual_categories)
    extra_dirs = set(actual_categories) - set(expected_categories)
    
    if missing_dirs:
        print("❌ MISSING directories:")
        for missing in missing_dirs:
            print(f"   📁 {missing}")
    else:
        print("✅ All expected directories exist!")
    
    if extra_dirs:
        print("⚠️  EXTRA directories (not in config):")
        for extra in extra_dirs:
            print(f"   📁 {extra}")

def create_missing_dirs():
    print()
    print("🛠️  CREATING MISSING DIRECTORIES")
    print("=" * 60)
    
    year = "year_1"
    term = "term_1"
    block = "block_1" 
    subject = "anatomy"
    
    base_path = os.path.join(CONFIG["data_dir"], year, term, block, subject)
    expected_categories = list(NAVIGATION_STRUCTURE[year]["terms"][term]["blocks"][block]["subjects"][subject]["categories"].keys())
    
    for category in expected_categories:
        category_path = os.path.join(base_path, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path, exist_ok=True)
            print(f"✅ Created: {category_path}")
        else:
            print(f"📁 Already exists: {category_path}")

if __name__ == "__main__":
    diagnose_structure()
    create_missing_dirs()