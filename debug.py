#!/usr/bin/env python3
"""
COMPREHENSIVE DEBUG SCRIPT FOR MEDICAL QUIZ BOT - ORGANIZED VERSION
Better error categorization and identification
"""
import os
import sys
import csv
import sqlite3
from pathlib import Path
from collections import defaultdict

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config directly to avoid fcntl dependency
try:
    import ast
    with open('config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
        config_tree = ast.parse(config_content)
        CONFIG = None
        NAVIGATION_STRUCTURE = None
        
        for node in config_tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if hasattr(target, 'id'):
                        if target.id == 'CONFIG':
                            CONFIG = ast.literal_eval(node.value)
                        elif target.id == 'NAVIGATION_STRUCTURE':
                            NAVIGATION_STRUCTURE = ast.literal_eval(node.value)
    
    if not CONFIG:
        CONFIG = {
            "data_dir": "data",
            "database_file": "quiz_bot.db", 
            "max_questions_per_quiz": 100,
            "time_between_questions": 1,
        }
        
except Exception as e:
    print(f"⚠️ Could not load config.py: {e}")
    CONFIG = {
        "data_dir": "data",
        "database_file": "quiz_bot.db",
        "max_questions_per_quiz": 100,
        "time_between_questions": 1,
    }
    NAVIGATION_STRUCTURE = {}

class OrganizedDebug:
    def __init__(self):
        self.errors = defaultdict(list)  # category -> list of errors
        self.warnings = defaultdict(list)
        self.successes = defaultdict(list)
        
    def log_error(self, category, message, details=None):
        error_data = {"message": message, "details": details}
        self.errors[category].append(error_data)
        print(f"❌ [{category}] {message}")
        if details:
            print(f"    📝 Details: {details}")
        
    def log_warning(self, category, message, details=None):
        warning_data = {"message": message, "details": details}
        self.warnings[category].append(warning_data)
        print(f"⚠️ [{category}] {message}")
        if details:
            print(f"    📝 Details: {details}")
        
    def log_success(self, category, message, details=None):
        success_data = {"message": message, "details": details}
        self.successes[category].append(success_data)
        print(f"✅ [{category}] {message}")
        if details:
            print(f"    📝 Details: {details}")
        
    def print_header(self, title, level=1):
        if level == 1:
            print(f"\n{'='*80}")
            print(f"🔍 {title.upper()}")
            print(f"{'='*80}")
        elif level == 2:
            print(f"\n{'─'*60}")
            print(f"📁 {title}")
            print(f"{'─'*60}")
        else:
            print(f"\n📂 {title}:")

    def print_category_summary(self, category, items, icon):
        if items:
            print(f"\n{icon} {category.upper()} ({len(items)} items):")
            for item in items[:5]:  # Show first 5
                print(f"   • {item['message']}")
                if item.get('details'):
                    print(f"     📝 {item['details']}")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")

    def print_comprehensive_summary(self):
        print(f"\n{'='*80}")
        print(f"📊 COMPREHENSIVE DEBUG SUMMARY")
        print(f"{'='*80}")
        
        total_errors = sum(len(errors) for errors in self.errors.values())
        total_warnings = sum(len(warnings) for warnings in self.warnings.values())
        total_successes = sum(len(successes) for successes in self.successes.values())
        
        print(f"\n📈 OVERALL STATS:")
        print(f"   ✅ Successes: {total_successes}")
        print(f"   ⚠️  Warnings: {total_warnings}") 
        print(f"   ❌ Errors: {total_errors}")
        
        # Print errors by category (most critical first)
        if self.errors:
            print(f"\n🚨 CRITICAL ERRORS BY CATEGORY:")
            for category in sorted(self.errors.keys(), key=lambda x: len(self.errors[x]), reverse=True):
                count = len(self.errors[category])
                print(f"\n   ❌ {category.upper()} ({count} errors):")
                for error in self.errors[category][:3]:  # Show top 3 per category
                    print(f"      • {error['message']}")
        
        # Print warnings by category
        if self.warnings:
            print(f"\n⚠️  WARNINGS BY CATEGORY:")
            for category in sorted(self.warnings.keys(), key=lambda x: len(self.warnings[x]), reverse=True):
                count = len(self.warnings[category])
                print(f"\n   ⚠️  {category.upper()} ({count} warnings):")
                for warning in self.warnings[category][:2]:  # Show top 2 per category
                    print(f"      • {warning['message']}")
        
        # Print successes by category
        if self.successes:
            print(f"\n✅ SUCCESSES BY CATEGORY:")
            for category in sorted(self.successes.keys(), key=lambda x: len(self.successes[x]), reverse=True):
                count = len(self.successes[category])
                print(f"\n   ✅ {category.upper()} ({count} successes)")

    def check_environment(self):
        """Check Python environment and dependencies"""
        self.print_header("Environment & Dependencies", 1)
        
        # Python version
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            self.log_success("environment", f"Python version: {sys.version.split()[0]}")
        else:
            self.log_error("environment", f"Python 3.8+ required", f"Found: {sys.version}")
            
        # Required packages
        try:
            import telegram
            self.log_success("dependencies", f"python-telegram-bot: {telegram.__version__}")
        except ImportError:
            self.log_error("dependencies", "python-telegram-bot not installed")
            
        # Token
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            masked_token = token[:4] + "..." + token[-4:] if len(token) > 8 else "***"
            self.log_success("environment", "Bot token found", f"Token: {masked_token}")
        else:
            self.log_error("environment", "Bot token not set", "Set TELEGRAM_BOT_TOKEN environment variable")

        # Platform
        if os.name == 'nt':
            self.log_success("environment", "Running on Windows")
        else:
            self.log_success("environment", "Running on Unix/Linux")

    def check_config_structure(self):
        """Check configuration structure"""
        self.print_header("Configuration Structure", 2)
        
        if not CONFIG:
            self.log_error("config", "CONFIG dictionary missing or empty")
            return
            
        required_configs = ['data_dir', 'database_file', 'max_questions_per_quiz', 'time_between_questions']
        for config in required_configs:
            if config in CONFIG:
                self.log_success("config", f"{config} configured", f"Value: {CONFIG[config]}")
            else:
                self.log_error("config", f"Missing required configuration", f"Missing: {config}")
                
        if NAVIGATION_STRUCTURE:
            years = list(NAVIGATION_STRUCTURE.keys())
            self.log_success("config", "Navigation structure loaded", f"Years: {years}")
            
            # Validate structure completeness
            for year, year_data in NAVIGATION_STRUCTURE.items():
                if 'display_name' not in year_data:
                    self.log_warning("config", f"Year missing display_name", f"Year: {year}")
                
                for term, term_data in year_data.get('terms', {}).items():
                    if 'display_name' not in term_data:
                        self.log_warning("config", f"Term missing display_name", f"Term: {term}")
        else:
            self.log_error("config", "NAVIGATION_STRUCTURE is empty")

    def check_file_system(self):
        """Check file and directory structure"""
        self.print_header("File System Structure", 2)
        
        data_dir = CONFIG.get('data_dir', 'data')
        if os.path.exists(data_dir):
            self.log_success("filesystem", "Data directory exists", data_dir)
        else:
            self.log_error("filesystem", "Data directory missing", f"Path: {data_dir}")
            return
            
        # Check module files
        modules = ['config.py', 'file_manager.py', 'callback_manager.py', 
                  'database.py', 'quiz_manager.py', 'handlers.py', 'main.py']
        missing_modules = []
        for module in modules:
            if os.path.exists(module):
                self.log_success("filesystem", f"Module file exists", module)
            else:
                missing_modules.append(module)
                self.log_error("filesystem", f"Module file missing", module)
                
        if missing_modules:
            self.log_error("filesystem", f"Missing {len(missing_modules)} module files", f"Files: {missing_modules}")

    def check_navigation_integrity(self):
        """Check navigation structure integrity"""
        self.print_header("Navigation Structure Integrity", 2)
        
        if not NAVIGATION_STRUCTURE:
            self.log_error("navigation", "No navigation structure to check")
            return
            
        total_missing_paths = 0
        total_missing_files = 0
        
        for year, year_data in NAVIGATION_STRUCTURE.items():
            year_path = os.path.join(CONFIG['data_dir'], year)
            
            if not os.path.exists(year_path):
                self.log_error("navigation", f"Year directory missing", f"Path: {year_path}")
                total_missing_paths += 1
                continue
                
            self.log_success("navigation", f"Year directory exists", f"Year: {year_data.get('display_name', year)}")
            
            for term, term_data in year_data.get('terms', {}).items():
                term_path = os.path.join(year_path, term)
                
                if not os.path.exists(term_path):
                    self.log_error("navigation", f"Term directory missing", f"Path: {term_path}")
                    total_missing_paths += 1
                    continue
                    
                for block, block_data in term_data.get('blocks', {}).items():
                    block_path = os.path.join(term_path, block)
                    
                    if not os.path.exists(block_path):
                        self.log_error("navigation", f"Block directory missing", f"Path: {block_path}")
                        total_missing_paths += 1
                        continue
                        
                    for subject, subject_data in block_data.get('subjects', {}).items():
                        subject_path = os.path.join(block_path, subject)
                        
                        if not os.path.exists(subject_path):
                            self.log_error("navigation", f"Subject directory missing", f"Path: {subject_path}")
                            total_missing_paths += 1
                            continue
                            
                        for category, category_data in subject_data.get('categories', {}).items():
                            category_path = os.path.join(subject_path, category)
                            
                            if not os.path.exists(category_path):
                                self.log_error("navigation", f"Category directory missing", f"Path: {category_path}")
                                total_missing_paths += 1
                                continue
                                
                            # Check CSV files in category
                            expected_files = list(category_data.get('subtopics', {}).keys())
                            actual_files = [f for f in os.listdir(category_path) if f.endswith('.csv')] if os.path.exists(category_path) else []
                            
                            for expected_file in expected_files:
                                if expected_file not in actual_files:
                                    self.log_error("navigation", f"CSV file missing", f"File: {expected_file} in {category_path}")
                                    total_missing_files += 1
                                else:
                                    self.log_success("navigation", f"CSV file exists", f"File: {expected_file}")
        
        if total_missing_paths > 0:
            self.log_error("navigation", f"Total missing directories", f"Count: {total_missing_paths}")
        if total_missing_files > 0:
            self.log_error("navigation", f"Total missing CSV files", f"Count: {total_missing_files}")

    def check_csv_quality(self):
        """Check CSV file quality and format"""
        self.print_header("CSV File Quality Check", 2)
        
        if not NAVIGATION_STRUCTURE:
            self.log_error("csv", "No navigation structure - cannot check CSV files")
            return
            
        files_checked = 0
        problematic_files = []
        
        for year, year_data in NAVIGATION_STRUCTURE.items():
            for term, term_data in year_data.get('terms', {}).items():
                for block, block_data in term_data.get('blocks', {}).items():
                    for subject, subject_data in block_data.get('subjects', {}).items():
                        for category, category_data in subject_data.get('categories', {}).items():
                            for csv_file in category_data.get('subtopics', {}).keys():
                                file_path = os.path.join(CONFIG['data_dir'], year, term, block, subject, category, csv_file)
                                files_checked += 1
                                
                                if not os.path.exists(file_path):
                                    problematic_files.append((csv_file, "FILE_MISSING"))
                                    continue
                                
                                # Validate CSV content
                                issues = self._validate_csv_file(file_path)
                                if issues:
                                    problematic_files.append((csv_file, issues))
                                else:
                                    self.log_success("csv", f"Valid CSV file", csv_file)
        
        # Report CSV issues
        for file, issue in problematic_files:
            if issue == "FILE_MISSING":
                self.log_error("csv", f"CSV file missing", file)
            else:
                self.log_error("csv", f"CSV file has issues", f"{file}: {issue}")
                
        self.log_success("csv", f"CSV check completed", f"Checked: {files_checked}, Problematic: {len(problematic_files)}")

    def _validate_csv_file(self, file_path):
        """Validate a single CSV file and return issues"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                valid_questions = 0
                
                for i, row in enumerate(reader, 1):
                    # Skip empty rows and comments
                    if not row or not any(row) or (row[0] and row[0].startswith('#')):
                        continue
                        
                    # Check column count
                    if len(row) < 6:
                        issues.append(f"Row {i}: Only {len(row)} columns")
                        continue
                        
                    # Check correct answer
                    if len(row[5].strip()) == 0:
                        issues.append(f"Row {i}: Empty correct answer")
                        continue
                        
                    correct_answer = row[5].strip().upper()
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        issues.append(f"Row {i}: Invalid answer '{row[5]}'")
                        continue
                        
                    valid_questions += 1
                
                if valid_questions == 0:
                    issues.append("No valid questions found")
                    
        except Exception as e:
            issues.append(f"Read error: {e}")
            
        return ", ".join(issues) if issues else None

    def check_specific_issues(self):
        """Check specific known problem areas"""
        self.print_header("Specific Problem Investigation", 2)
        
        # MIDTERM CATEGORY SPECIFIC CHECK
        self.print_header("Midterm Category Investigation", 3)
        
        midterm_path = "data/year_1/term_1/block_1/anatomy/Midterm"
        expected_files = ["01_Midterm Questions.csv", "02_Midterm Questions.csv", "03_Midterm Questions.csv"]
        
        if not os.path.exists(midterm_path):
            self.log_error("midterm", "MIDTERM DIRECTORY MISSING", 
                          "This is likely causing your 'No quizzes available' error")
            self.log_warning("midterm", "Suggested fix", 
                           "Create directory: data/year_1/term_1/block_1/anatomy/Midterm/")
        else:
            self.log_success("midterm", "Midterm directory exists", midterm_path)
            
            actual_files = os.listdir(midterm_path)
            csv_files = [f for f in actual_files if f.endswith('.csv')]
            
            if not csv_files:
                self.log_error("midterm", "No CSV files in Midterm directory",
                              "Add CSV files to fix the issue")
            else:
                self.log_success("midterm", f"Found {len(csv_files)} CSV files", f"Files: {csv_files}")
            
            # Check each expected file
            for expected_file in expected_files:
                if expected_file in actual_files:
                    self.log_success("midterm", f"Expected file found", expected_file)
                else:
                    self.log_error("midterm", f"Expected file missing", expected_file)
                    
            # Check for case sensitivity issues
            lower_files = [f.lower() for f in actual_files]
            for expected_file in expected_files:
                if expected_file.lower() in lower_files and expected_file not in actual_files:
                    self.log_error("midterm", f"Case sensitivity issue", 
                                  f"Expected: {expected_file}, Found: {[f for f in actual_files if f.lower() == expected_file.lower()][0]}")

        # CHECK OTHER COMMON ISSUES
        self.print_header("Other Common Issues", 3)
        
        # Check if data directory has correct case
        data_dir = CONFIG.get('data_dir', 'data')
        if os.path.exists(data_dir):
            actual_case = [d for d in os.listdir('.') if d.lower() == data_dir.lower()][0]
            if actual_case != data_dir:
                self.log_error("case", "Data directory case mismatch", 
                              f"Config expects: '{data_dir}', Found: '{actual_case}'")
        
        # Check database
        db_file = CONFIG.get('database_file', 'quiz_bot.db')
        if os.path.exists(db_file):
            self.log_success("database", "Database file exists", db_file)
        else:
            self.log_warning("database", "Database file will be created", db_file)

    def generate_action_plan(self):
        """Generate a specific action plan based on findings"""
        print(f"\n{'='*80}")
        print(f"🎯 ACTION PLAN & SOLUTIONS")
        print(f"{'='*80}")
        
        if not self.errors:
            print(f"\n🎉 No critical errors found! Your bot should work correctly.")
            return
            
        # Priority 1: File system errors
        if self.errors.get('filesystem'):
            print(f"\n🚨 PRIORITY 1: FIX FILE SYSTEM ERRORS")
            for error in self.errors['filesystem']:
                print(f"   • {error['message']}")
                if error.get('details'):
                    print(f"     💡 Solution: {error['details']}")
        
        # Priority 2: Navigation structure errors  
        if self.errors.get('navigation'):
            print(f"\n🚨 PRIORITY 2: FIX NAVIGATION STRUCTURE")
            missing_dirs = [e for e in self.errors['navigation'] if 'directory missing' in e['message'].lower()]
            missing_files = [e for e in self.errors['navigation'] if 'csv file missing' in e['message'].lower()]
            
            if missing_dirs:
                print(f"   📁 CREATE MISSING DIRECTORIES:")
                for error in missing_dirs[:5]:  # Show first 5
                    print(f"      • {error['details']}")
                    
            if missing_files:
                print(f"   📄 CREATE MISSING CSV FILES:")
                for error in missing_files[:5]:
                    print(f"      • {error['details']}")
        
        # Priority 3: Midterm-specific fixes
        if self.errors.get('midterm'):
            print(f"\n🚨 PRIORITY 3: FIX MIDTERM CATEGORY (Your reported issue)")
            for error in self.errors['midterm']:
                print(f"   • {error['message']}")
                if error.get('details'):
                    print(f"     💡 {error['details']}")
            
            print(f"\n   🛠️  QUICK FIX FOR MIDTERM:")
            print(f"      1. Create directory: mkdir data\\year_1\\term_1\\block_1\\anatomy\\Midterm")
            print(f"      2. Add CSV files to the directory")
            print(f"      3. Ensure files are named exactly as in config.py")
        
        # Priority 4: Configuration issues
        if self.errors.get('config'):
            print(f"\n⚠️  PRIORITY 4: FIX CONFIGURATION")
            for error in self.errors['config']:
                print(f"   • {error['message']}")
        
        # Priority 5: CSV quality issues
        if self.errors.get('csv'):
            print(f"\n⚠️  PRIORITY 5: FIX CSV FORMAT ISSUES")
            for error in self.errors['csv'][:3]:  # Show first 3
                print(f"   • {error['message']}")
                if error.get('details'):
                    print(f"     📝 {error['details']}")

    def run_all_checks(self):
        """Run all diagnostic checks"""
        print("🚀 COMPREHENSIVE DEBUG - ORGANIZED VERSION")
        print("This will identify and categorize all issues in your Medical Quiz Bot")
        
        self.check_environment()
        self.check_config_structure()
        self.check_file_system()
        self.check_navigation_integrity()
        self.check_csv_quality()
        self.check_specific_issues()
        
        self.print_comprehensive_summary()
        self.generate_action_plan()

if __name__ == "__main__":
    debug = OrganizedDebug()
    debug.run_all_checks()