"""
Check available PDF content
"""
from pdf_manager import PDFManager

def check_pdf_content():
    pdf_manager = PDFManager()
    
    print("📊 PDF Knowledge Base Status:")
    print(f"Available subjects: {pdf_manager.list_available_subjects()}")
    
    if "histology" in pdf_manager.list_available_subjects():
        print("\n🔬 Histology PDFs loaded:")
        histology_pdfs = pdf_manager.get_pdf_info("histology")
        for pdf in histology_pdfs:
            print(f"  • {pdf}")
        
        # Test search
        print("\n🔍 Testing search functionality:")
        results = pdf_manager.search_pdf("cell membrane", "histology", top_k=2)
        print(f"Found {len(results)} results for 'cell membrane'")
        for result in results:
            print(f"  • Source: {result['source']} (Page {result['page']})")
            print(f"    Text: {result['text'][:100]}...")

if __name__ == "__main__":
    check_pdf_content()