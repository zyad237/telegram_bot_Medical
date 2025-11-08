"""
Script to initialize college PDF system with histology
"""
import os
from pdf_manager import PDFManager
from college_config import COLLEGE_PDFS

def setup_college_pdfs():
    pdf_manager = PDFManager()
    
    print("📚 Setting up college PDF knowledge base...")
    
    for subject, pdfs in COLLEGE_PDFS.items():
        print(f"\n🔧 Processing {subject}...")
        
        # Add primary textbook
        primary_pdf = pdfs.get("primary_textbook")
        if primary_pdf:
            pdf_path = f"college_pdfs/{primary_pdf}"
            if os.path.exists(pdf_path):
                success = pdf_manager.add_pdf(pdf_path, subject)
                if success:
                    print(f"✅ Added primary textbook: {primary_pdf}")
                else:
                    print(f"❌ Failed to add: {primary_pdf}")
            else:
                print(f"⚠️ PDF not found: {pdf_path}")
        
        # Add lecture notes
        for note in pdfs.get("lecture_notes", []):
            note_path = f"college_pdfs/{note}"
            if os.path.exists(note_path):
                success = pdf_manager.add_pdf(note_path, subject)
                if success:
                    print(f"✅ Added lecture note: {note}")
                else:
                    print(f"❌ Failed to add: {note}")
            else:
                print(f"⚠️ Lecture note not found: {note_path}")
    
    print(f"\n🎉 Setup complete! Available subjects: {pdf_manager.list_available_subjects()}")
    
    # Test the histology content
    if "histology" in pdf_manager.list_available_subjects():
        print("\n🧪 Testing histology content...")
        test_queries = [
            "cell membrane structure",
            "mitochondria function", 
            "epithelial tissue types",
            "connective tissue components"
        ]
        
        for query in test_queries:
            results = pdf_manager.search_pdf(query, "histology", top_k=1)
            if results:
                print(f"✅ '{query}': Found {len(results)} results")
            else:
                print(f"❌ '{query}': No results")

if __name__ == "__main__":
    setup_college_pdfs()