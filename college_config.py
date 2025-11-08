"""
College-specific configuration - UPDATED WITH HISTOLOGY PDF
"""
import os

# Your college PDF structure - UPDATED
COLLEGE_PDFS = {
    "anatomy": {
        "primary_textbook": "college_anatomy_handbook.pdf",
        "lecture_notes": [
            "anatomy_lecture_1.pdf",
            "anatomy_lecture_2.pdf", 
            "musculoskeletal_notes.pdf"
        ],
        "practical_guides": [
            "dissection_guide.pdf",
            "anatomy_practical.pdf"
        ]
    },
    "histology": {
        "primary_textbook": "histology all.pdf",  # ADDED YOUR PDF
        "lecture_notes": [
            "histology_cell_structure.pdf",
            "tissue_types_notes.pdf"
        ],
        "slide_atlas": [
            "histology_slides_guide.pdf"
        ]
    },
    "biochemistry": {
        "primary_textbook": "college_biochemistry.pdf",
        "lecture_notes": [
            "metabolism_notes.pdf",
            "enzymes_biochem.pdf"
        ]
    },
    "physiology": {
        "primary_textbook": "college_physiology.pdf", 
        "lecture_notes": [
            "cardiovascular_physio.pdf",
            "neurophysiology_notes.pdf"
        ]
    }
}

# College-specific subject mapping
SUBJECT_MAPPING = {
    "anatomy": "Anatomy",
    "histology": "Histology", 
    "biochemistry": "Biochemistry",
    "physiology": "Physiology",
    "pathology": "Pathology",
    "pharmacology": "Pharmacology"
}

def get_college_pdf_path(subject: str, pdf_type: str = "primary_textbook") -> str:
    """Get path to college PDF file"""
    if subject in COLLEGE_PDFS and pdf_type in COLLEGE_PDFS[subject]:
        pdf_name = COLLEGE_PDFS[subject][pdf_type]
        if isinstance(pdf_name, list):
            pdf_name = pdf_name[0]  # Take first one
        return os.path.join("college_pdfs", pdf_name)
    return None

def get_available_subjects() -> list:
    """Get list of subjects with college PDFs"""
    return list(COLLEGE_PDFS.keys())