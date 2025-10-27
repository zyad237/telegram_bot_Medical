#!/usr/bin/env python3
"""
Debug script to check file discovery for nested structure
"""
import os
from config import CONFIG, TOPIC_DISPLAY_NAMES, NESTED_STRUCTURE

print("🔍 DEBUG FILE DISCOVERY - NESTED STRUCTURE")
print("=" * 60)

# Check data directory
data_dir = CONFIG["data_dir"]
print(f"Data directory: {data_dir}")
print(f"Exists: {os.path.exists(data_dir)}")

if os.path.exists(data_dir):
    print(f"Contents: {os.listdir(data_dir)}")

print("\n📊 CONFIGURATION CHECK")
print("=" * 60)
print(f"TOPIC_DISPLAY_NAMES: {TOPIC_DISPLAY_NAMES}")
print(f"NESTED_STRUCTURE: {NESTED_STRUCTURE}")

print("\n📁 NESTED FILE STRUCTURE CHECK")
print("=" * 60)

for topic in TOPIC_DISPLAY_NAMES:
    topic_path = os.path.join(data_dir, topic)
    print(f"\n🎯 TOPIC: {topic}")
    print(f"   Path: {topic_path}")
    print(f"   Exists: {os.path.exists(topic_path)}")
    
    if not os.path.exists(topic_path):
        print(f"   ❌ Topic directory does not exist!")
        continue
    
    # Check categories for this topic
    categories = os.listdir(topic_path)
    print(f"   Categories found: {categories}")
    
    for category in categories:
        category_path = os.path.join(topic_path, category)
        print(f"\n   📂 CATEGORY: {category}")
        print(f"      Path: {category_path}")
        print(f"      Exists: {os.path.exists(category_path)}")
        
        if not os.path.exists(category_path) or not os.path.isdir(category_path):
            print(f"      ❌ Category directory does not exist or is not a directory!")
            continue
        
        # Check if category is in config
        if (topic in NESTED_STRUCTURE and 
            category in NESTED_STRUCTURE[topic]):
            print(f"      ✅ Category '{category}' is in NESTED_STRUCTURE")
            category_config = NESTED_STRUCTURE[topic][category]
        else:
            print(f"      ❌ Category '{category}' NOT in NESTED_STRUCTURE")
            continue
        
        # Check CSV files in this category
        csv_files = [f for f in os.listdir(category_path) if f.endswith('.csv')]
        print(f"      CSV files found: {csv_files}")
        
        if not csv_files:
            print(f"      ⚠️ No CSV files in this category")
            continue
        
        for csv_file in csv_files:
            subtopic = csv_file[:-4]  # Remove .csv extension
            print(f"\n      📄 CSV: {csv_file}")
            print(f"         Subtopic name: '{subtopic}'")
            
            # Check if subtopic is in config
            if ("subtopics" in category_config and 
                subtopic in category_config["subtopics"]):
                print(f"         ✅ IN CONFIG - Display name: '{category_config['subtopics'][subtopic]}'")
            else:
                print(f"         ❌ NOT IN CONFIG")
                if "subtopics" in category_config:
                    print(f"         Available subtopics in config: {list(category_config['subtopics'].keys())}")

print("\n🔧 CONFIGURATION SUMMARY")
print("=" * 60)
print("Topics and their structure from config:")
for topic, topic_data in NESTED_STRUCTURE.items():
    print(f"\n{topic}:")
    for category, category_data in topic_data.items():
        print(f"  └── {category} ('{category_data['display_name']}'):")
        if "subtopics" in category_data:
            for subtopic, display_name in category_data["subtopics"].items():
                print(f"      └── {subtopic} → '{display_name}'")