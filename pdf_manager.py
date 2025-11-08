"""
PDF management for college-specific textbooks and materials
"""
import os
import logging
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional
import pickle

logger = logging.getLogger(__name__)

class PDFManager:
    def __init__(self):
        self.pdf_dir = "college_pdfs"
        self.embeddings_dir = "pdf_embeddings"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.pdf_data = {}
        
        # Create directories if they don't exist
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)
        
        self.load_or_create_index()
    
    def load_or_create_index(self):
        """Load existing PDF index or create new one"""
        index_path = os.path.join(self.embeddings_dir, "pdf_index.faiss")
        data_path = os.path.join(self.embeddings_dir, "pdf_data.pkl")
        
        if os.path.exists(index_path) and os.path.exists(data_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(data_path, 'rb') as f:
                    self.pdf_data = pickle.load(f)
                logger.info("✅ Loaded existing PDF index")
            except Exception as e:
                logger.error(f"❌ Error loading index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        self.index = faiss.IndexFlatL2(384)  # Dimension for all-MiniLM-L6-v2
        self.pdf_data = {
            'texts': [],
            'sources': [],
            'pages': [],
            'subjects': []
        }
        logger.info("✅ Created new PDF index")
    
    def add_pdf(self, pdf_path: str, subject: str, description: str = ""):
        """Add a college PDF to the knowledge base"""
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"❌ PDF not found: {pdf_path}")
                return False
            
            # Extract text from PDF
            text_chunks = self._extract_text_from_pdf(pdf_path)
            
            if not text_chunks:
                logger.error(f"❌ No text extracted from PDF: {pdf_path}")
                return False
            
            # Create embeddings for each chunk
            for page_num, chunk in text_chunks:
                embedding = self.model.encode([chunk])
                self.index.add(embedding.astype('float32'))
                
                # Store metadata
                self.pdf_data['texts'].append(chunk)
                self.pdf_data['sources'].append(os.path.basename(pdf_path))
                self.pdf_data['pages'].append(page_num)
                self.pdf_data['subjects'].append(subject)
            
            self._save_index()
            logger.info(f"✅ Added PDF: {os.path.basename(pdf_path)} for subject: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding PDF {pdf_path}: {e}")
            return False
    
    def _extract_text_from_pdf(self, pdf_path: str) -> List[tuple]:
        """Extract text from PDF and chunk it"""
        text_chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():  # Only process non-empty pages
                        # Clean and chunk text
                        chunks = self._chunk_text(text, chunk_size=500, overlap=50)
                        
                        for chunk in chunks:
                            text_chunks.append((page_num + 1, chunk))
            
            return text_chunks
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF: {e}")
            return []
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        if not words:
            return chunks
            
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def search_pdf(self, query: str, subject: str = None, top_k: int = 3) -> List[Dict]:
        """Search for relevant content in college PDFs"""
        try:
            if self.index.ntotal == 0:
                return []
                
            # Encode query
            query_embedding = self.model.encode([query]).astype('float32')
            
            # Search index
            distances, indices = self.index.search(query_embedding, top_k * 3)
            
            results = []
            seen_texts = set()
            
            for i, idx in enumerate(indices[0]):
                if idx < len(self.pdf_data['texts']):
                    result_subject = self.pdf_data['subjects'][idx]
                    
                    # Filter by subject if specified
                    if subject and result_subject != subject:
                        continue
                    
                    text = self.pdf_data['texts'][idx]
                    source = self.pdf_data['sources'][idx]
                    page = self.pdf_data['pages'][idx]
                    
                    # Avoid duplicates
                    if text not in seen_texts:
                        results.append({
                            'text': text,
                            'source': source,
                            'page': page,
                            'subject': result_subject,
                            'distance': distances[0][i]
                        })
                        seen_texts.add(text)
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching PDFs: {e}")
            return []
    
    def get_subject_context(self, query: str, subject: str, top_k: int = 3) -> str:
        """Get relevant PDF context for a subject"""
        results = self.search_pdf(query, subject, top_k)
        
        if not results:
            return f"No specific information found in college materials for {subject}."
        
        context = f"**Relevant content from college {subject} materials:**\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"**Source:** {result['source']} (Page {result['page']})\n"
            context += f"**Content:** {result['text']}\n\n"
        
        return context
    
    def list_available_subjects(self) -> List[str]:
        """List all subjects with available PDFs"""
        return list(set(self.pdf_data.get('subjects', [])))
    
    def get_pdf_info(self, subject: str) -> List[str]:
        """Get PDF files available for a subject"""
        subject_pdfs = []
        for i, subj in enumerate(self.pdf_data.get('subjects', [])):
            if subj == subject:
                source = self.pdf_data['sources'][i]
                if source not in subject_pdfs:
                    subject_pdfs.append(source)
        return subject_pdfs
    
    def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            faiss.write_index(self.index, os.path.join(self.embeddings_dir, "pdf_index.faiss"))
            with open(os.path.join(self.embeddings_dir, "pdf_data.pkl"), 'wb') as f:
                pickle.dump(self.pdf_data, f)
            logger.info("✅ Saved PDF index")
        except Exception as e:
            logger.error(f"❌ Error saving index: {e}")