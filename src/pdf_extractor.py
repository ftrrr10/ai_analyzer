"""
PDF Extraction Module
Handles extraction of text from PDF files using PyMuPDF and OCR
"""
import os
from typing import Optional
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class PDFExtractor:
    """Handles PDF text extraction with multiple strategies"""
    
    def __init__(self):
        self.min_text_threshold = 100  # Minimum characters for digital extraction
    
    def extract_text_digital(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from digital PDF using PyMuPDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if failed
        """
        try:
            print(f"  → Trying digital extraction (PyMuPDF)...")
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text += page.get_text()
                print(f"    Page {page_num + 1}/{len(doc)}: {len(page.get_text())} chars")
            
            doc.close()
            
            if len(text.strip()) >= self.min_text_threshold:
                print(f"  ✓ Digital extraction successful: {len(text)} characters")
                return text.strip()
            else:
                print(f"  ⚠ Digital extraction yielded minimal text: {len(text)} chars")
                return None
                
        except Exception as e:
            print(f"  ✗ Error in digital extraction: {e}")
            return None
    
    def extract_text_ocr(self, pdf_path: str, language: str = 'ind') -> Optional[str]:
        """
        Extract text from scanned PDF using OCR (Tesseract)
        
        Args:
            pdf_path: Path to PDF file
            language: Language code for OCR (default: 'ind' for Indonesian)
            
        Returns:
            Extracted text or None if failed
        """
        try:
            print(f"  → Trying OCR extraction (Tesseract)...")
            
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            text = ""
            
            # OCR each page
            for i, image in enumerate(images):
                print(f"    Processing page {i+1}/{len(images)} with OCR...")
                page_text = pytesseract.image_to_string(image, lang=language)
                text += page_text + "\n\n"
                print(f"    Page {i+1}: {len(page_text)} chars extracted")
            
            if len(text.strip()) >= self.min_text_threshold:
                print(f"  ✓ OCR extraction successful: {len(text)} characters")
                return text.strip()
            else:
                print(f"  ⚠ OCR extraction yielded minimal text: {len(text)} chars")
                return None
                
        except Exception as e:
            print(f"  ✗ Error in OCR extraction: {e}")
            return None
    
    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Smart extraction: Try digital first, fallback to OCR
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text or None if all methods failed
        """
        print(f"\n📄 Extracting text from: {os.path.basename(pdf_path)}")
        
        if not os.path.exists(pdf_path):
            print(f"✗ File not found: {pdf_path}")
            return None
        
        # Try digital extraction first
        text = self.extract_text_digital(pdf_path)
        
        if text and len(text.strip()) >= self.min_text_threshold:
            return text
        
        # Fallback to OCR if digital extraction failed or yielded little text
        print("  → Digital extraction insufficient, falling back to OCR...")
        text = self.extract_text_ocr(pdf_path)
        
        if text:
            return text
        
        print("✗ All extraction methods failed")
        return None
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata information
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                'num_pages': len(doc),
                'file_size': os.path.getsize(pdf_path),
                'metadata': doc.metadata,
                'is_encrypted': doc.is_encrypted
            }
            doc.close()
            return info
        except Exception as e:
            print(f"Error getting PDF info: {e}")
            return {}
