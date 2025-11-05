# [file name]: init_navigation.py
"""
Initialize navigation structure at startup
"""
import logging
from auto_navigator import AutoNavigator
from config import CONFIG

logger = logging.getLogger(__name__)

def initialize_navigation():
    """Initialize the navigation structure and update config"""
    print("🔄 Building navigation structure from data directory...")
    
    # Build navigation structure
    NAVIGATION_STRUCTURE = AutoNavigator.build_navigation_structure(CONFIG["data_dir"])
    
    if NAVIGATION_STRUCTURE:
        print("✅ Navigation structure built successfully!")
        AutoNavigator.print_structure(NAVIGATION_STRUCTURE)
        
        # Update the config module
        import config
        config.NAVIGATION_STRUCTURE = NAVIGATION_STRUCTURE
        return True
    else:
        print("❌ Failed to build navigation structure!")
        print("💡 Make sure your data directory structure is:")
        print("   data/")
        print("   ├── year_1/")
        print("   │   ├── anatomy/")
        print("   │   │   ├── general/")
        print("   │   │   │   ├── 01_Introduction to Anatomy.csv")
        print("   │   │   │   └── ...")
        print("   │   │   ├── midterm/")
        print("   │   │   │   ├── 01_Midterm Questions.csv")
        print("   │   │   │   └── ...")
        print("   │   │   └── ...")
        print("   │   └── histology/")
        print("   │       ├── general/")
        print("   │       │   ├── 01_Paraffin technique.csv")
        print("   │       │   └── ...")
        print("   │       └── ...")
        print("   └── ...")
        return False

# Initialize when imported
NAVIGATION_STRUCTURE = {}
if initialize_navigation():
    NAVIGATION_STRUCTURE = AutoNavigator.build_navigation_structure(CONFIG["data_dir"])
