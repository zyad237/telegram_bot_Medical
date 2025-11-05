#!/usr/bin/env python3
"""
Check CSV file format
"""
import csv
import os

def check_csv(file_path):
    print(f"\n🔍 Checking: {file_path}")
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader, 1):
                print(f"Row {i}: {row}")
                if len(row) < 6:
                    print(f"  ❌ Only {len(row)} columns (need 6)")
                else:
                    print(f"  ✅ 6 columns found")
                    print(f"     Q: {row[0]}")
                    print(f"     A: {row[1]}")
                    print(f"     B: {row[2]}")
                    print(f"     C: {row[3]}")
                    print(f"     D: {row[4]}")
                    print(f"     Correct: {row[5]}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

# Check your specific file
check_csv("data/anatomy/3Rd_Month_To_Placenta.csv")