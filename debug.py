#!/usr/bin/env python3
"""
Debug script to check file discovery
"""
import os
from config import CONFIG, TOPIC_DISPLAY_NAMES, SUBPROJECT_DISPLAY_NAMES

print("🔍 DEBUG FILE DISCOVERY")
print("=" * 50)

# Check data directory
data_dir = CONFIG["data_dir"]
print(f"Data directory: {data_dir}")
print(f"Exists: {os.path.exists(data_dir)}")

if os.path.exists(data_dir):
    print(f"Contents: {os.listdir(data_dir)}")

print("\n📊 CONFIGURATION CHECK")
print("=" * 50)
print(f"TOPIC_DISPLAY_NAMES: {TOPIC_DISPLAY_NAMES}")
print(f"SUBPROJECT_DISPLAY_NAMES: {SUBPROJECT_DISPLAY_NAMES}")

print("\n📁 FILE STRUCTURE CHECK")
print("=" * 50)
for topic in TOPIC_DISPLAY_NAMES:
    topic_path = os.path.join(data_dir, topic)
    print(f"\nTopic: {topic}")
    print(f"Path: {topic_path}")
    print(f"Exists: {os.path.exists(topic_path)}")
    
    if os.path.exists(topic_path):
        files = os.listdir(topic_path)
        print(f"Files: {files}")
        
        for file in files:
            if file.endswith('.csv'):
                subtopic = file[:-4]
                print(f"  CSV: {file} -> subtopic: '{subtopic}'")
                if topic in SUBPROJECT_DISPLAY_NAMES:
                    if subtopic in SUBPROJECT_DISPLAY_NAMES[topic]:
                        print(f"    ✅ IN CONFIG")
                    else:
                        print(f"    ❌ NOT IN CONFIG")