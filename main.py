import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
# Cek jika 'src' sudah ada di path (untuk menghindari duplikasi jika diimpor)
current_path = str(Path(__file__).parent.resolve())
if current_path not in sys.path:
    sys.path.insert(0, current_path)

try:
    from src.database import DatabaseManager
    from src.pdf_extractor import PDFExtractor
    from src.ai_analyzer import LegalAIAnalyzer
    from src.models import Complaint, AnalysisResult, LegalArticle, Recommendation
    from utils.helpers import (
        generate_complaint_number,
        sanitize_filename,
        print_separator,
        print_section_header
    )
except ImportError as e:
    print(f"Error: Gagal mengimpor modul. Pastikan semua file ada di 'src/' dan 'utils/'. Error: {e}")
    sys.exit(1)


class LegalComplaintProcessor:
    """Main processor for legal complaints"""
    
    def __init__(self):
        """Initialize all components"""
        print("🚀 Initializing Legal Complaint Analyzer...")
        
        self.db = DatabaseManager()
        self.pdf_extractor = PDFExtractor()
        self.ai_analyzer = LegalAIAnalyzer()
        
        print("✓ All components initialized\n")
    
    def process_complaint(self, pdf_path: str, uploaded_by: str = 'system') -> dict:
        """
        Complete processing pipeline for a complaint
        
        Args:
            pdf_path: Path to PDF file
            uploaded_by: Username of uploader
            
        Returns:
            Dictionary with processing results
        """
        print_section_header("LEGAL COMPLAINT ANALYZER - PROCESSING PIPELINE")
        
        # Validate file exists
        if not os.path.exists(pdf_path):
            print(f"✗ File not found: {pdf_path}")
            return {'success': False, 'error': 'File not found'}
        
        start_time = datetime.now()
        complaint_id = None # Inisialisasi jika gagal di langkah awal
        analysis_id = None
        
        try:
            # ═══════════════════════════════════════════════════════
            # STEP 1: Extract Text from PDF
            # ═══════════════════════════════════════════════════════
            print_section_header("STEP 1: PDF TEXT EXTRACTION")
            
            extracted_text = self.pdf_extractor.extract_text(pdf_path)
            
            if not extracted_text:
                print("✗ Failed to extract text from PDF")
                return {'success': False, 'error': 'Text extraction failed'}
            
            print(f"✓ Extracted {len(extracted_text)} characters")
            print(f"✓ Preview: {extracted_text[:200]}...\n")
            
            # ═══════════════════════════════════════════════════════
            # STEP 2: Create Complaint Record
            # ═══════════════════════════════════════════════════════
            print_section_header("STEP 2: SAVING COMPLAINT TO DATABASE")
            
            complaint_number = generate_complaint_number()
            pdf_filename = sanitize_filename(os.path.basename(pdf_path))
            
            complaint = Complaint(
                complaint_number=complaint_number,
                pdf_filename=pdf_filename,
                pdf_path=pdf_path, # Path di server sementara
                extracted_text=extracted_text,
                status='processing',
                uploaded_by=uploaded_by
            )
            
            complaint_data = self.db.create_complaint(complaint)
            complaint_id = complaint_data['id']
            
            # Log action
            self.db.log_action(
                complaint_id=complaint_id,
                analysis_id=None,
                action='COMPLAINT_UPLOADED',
                action_by=uploaded_by,
                details=f'PDF: {pdf_filename}'
            )
            
            print(f"✓ Complaint saved with ID: {complaint_id}")
            print(f"✓ Complaint number: {complaint_number}\n")
            
            # ═══════════════════════════════════════════════════════
            # STEP 3: AI Analysis
            # ═══════════════════════════════════════════════════════
            print_section_header("STEP 3: AI ANALYSIS")
            
            analysis_result = self.ai_analyzer.analyze(extracted_text)
            
            if not analysis_result:
                print("✗ AI analysis failed")
                self.db.update_complaint_status(complaint_id, 'error')
                return {'success': False, 'error': 'AI analysis failed'}
            
            print("✓ AI analysis completed successfully\n")
            
            # ═══════════════════════════════════════════════════════
            # STEP 4: Save Analysis Results
            # ═══════════════════════════════════════════════════════
            print_section_header("STEP 4: SAVING ANALYSIS RESULTS")
            
            # Prepare analysis model
            analysis_model = AnalysisResult(
                complaint_id=complaint_id,
                pelapor_nama=analysis_result.get('pelapor', {}).get('nama'),
                pelapor_ktp=analysis_result.get('pelapor', {}).get('ktp'),
                pelapor_kontak=analysis_result.get('pelapor', {}).get('kontak'),
                terlapor_nama=analysis_result.get('terlapor', {}).get('nama'),
                terlapor_identitas=analysis_result.get('terlapor', {}).get('identitas'),
                terlapor_ciri=analysis_result.get('terlapor', {}).get('ciri'),
                kejadian_tanggal=analysis_result.get('kejadian', {}).get('tanggal'),
                kejadian_waktu=analysis_result.get('kejadian', {}).get('waktu'),
                kejadian_lokasi=analysis_result.get('kejadian', {}).get('lokasi'),
                kejadian_provinsi=analysis_result.get('kejadian', {}).get('provinsi'),
                kronologi=analysis_result.get('kronologi'),
                jenis_kasus=analysis_result.get('jenis_kasus'),
                kerugian_materil=analysis_result.get('kerugian', {}).get('materil'),
                kerugian_immateril=analysis_result.get('kerugian', {}).get('immateril'),
                bukti_fisik=analysis_result.get('bukti', {}).get('fisik'),
                bukti_dokumen=analysis_result.get('bukti', {}).get('dokumen'),
                bukti_saksi=analysis_result.get('bukti', {}).get('saksi'),
                bukti_digital=analysis_result.get('bukti', {}).get('digital'),
                executive_summary=analysis_result.get('summary', {}).get('executive_summary'),
                key_points=analysis_result.get('summary', {}).get('key_points'),
                tingkat_urgensi=analysis_result.get('summary', {}).get('tingkat_urgensi'),
                alasan_urgensi=analysis_result.get('summary', {}).get('alasan_urgensi'),
                missing_information=analysis_result.get('summary', {}).get('missing_information'),
                kelengkapan_laporan=analysis_result.get('quality', {}).get('kelengkapan_laporan'),
                kualitas_bukti=analysis_result.get('quality', {}).get('kualitas_bukti'),
                kompleksitas_kasus=analysis_result.get('quality', {}).get('kompleksitas_kasus'),
                full_analysis_json=analysis_result,
                analyzed_by='AI-Gemini',
                analysis_duration_seconds=analysis_result.get('_metadata', {}).get('analysis_duration_seconds')
            )
            
            analysis_data = self.db.create_analysis_result(analysis_model)
            analysis_id = analysis_data['id']
            
            # ═══════════════════════════════════════════════════════
            # STEP 5: Save Legal Articles
            # ═══════════════════════════════════════════════════════
            print("\n💼 Saving legal articles...")
            
            articles_to_save = analysis_result.get('pasal_utama', []) + analysis_result.get('pasal_alternatif', [])
            
            for i, article_data in enumerate(articles_to_save):
                # Tentukan tipe artikel jika tidak ada
                article_type = article_data.get('article_type')
                if not article_type:
                    article_type = 'utama' if i < len(analysis_result.get('pasal_utama', [])) else 'alternatif'

                # Tentukan is_primary
                is_primary = article_data.get('is_primary', (article_type == 'utama'))

                article = LegalArticle(
                    analysis_id=analysis_id,
                    pasal_number=article_data.get('pasal_number'),
                    sumber_hukum=article_data.get('sumber_hukum'),
                    judul_pasal=article_data.get('judul_pasal'),
                    bunyi_pasal=article_data.get('bunyi_pasal'),
                    elemen_konstitutif=article_data.get('elemen_konstitutif'),
                    elemen_terpenuhi=article_data.get('elemen_terpenuhi'),
                    confidence_score=article_data.get('confidence_score', 0.5),
                    confidence_level=article_data.get('confidence_level', 'Sedang'),
                    reasoning=article_data.get('reasoning') or article_data.get('alasan'),
                    is_primary=is_primary,
                    article_type=article_type
                )
                self.db.create_legal_article(article)
            
            print(f"✓ Saved {len(articles_to_save)} legal articles")
            
            # ═══════════════════════════════════════════════════════
            # STEP 6: Save Recommendations
            # ═══════════════════════════════════════════════════════
            print("\n📋 Saving recommendations...")
            
            for rec_data in analysis_result.get('recommendations', []):
                recommendation = Recommendation(
                    analysis_id=analysis_id,
                    recommendation_text=rec_data.get('text'),
                    priority=rec_data.get('priority', 'Normal'),
                    category=rec_data.get('category')
                )
                self.db.create_recommendation(recommendation)
            
            print(f"✓ Saved {len(analysis_result.get('recommendations', []))} recommendations")
            
            # ═══════════════════════════════════════════════════════
            # STEP 7: Update Status & Log
            # ═══════════════════════════════════════════════════════
            self.db.update_complaint_status(complaint_id, 'analyzed')
            self.db.log_action(
                complaint_id=complaint_id,
                analysis_id=analysis_id,
                action='ANALYSIS_COMPLETED',
                action_by='system',
                details=f'Analysis ID: {analysis_id}'
            )
            
            # ═══════════════════════════════════════════════════════
            # FINAL SUMMARY
            # ═══════════════════════════════════════════════════════
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            print_section_header("✅ PROCESSING COMPLETE")
            print(f"Complaint Number  : {complaint_number}")
            print(f"Complaint ID      : {complaint_id}")
            print(f"Analysis ID       : {analysis_id}")
            print(f"Pelapor           : {analysis_result.get('pelapor', {}).get('nama', 'N/A')}")
            print(f"Jenis Kasus       : {analysis_result.get('jenis_kasus', 'N/A')}")
            print(f"Tingkat Urgensi   : {analysis_result.get('summary', {}).get('tingkat_urgensi', 'N/A')}")
            print(f"Pasal Utama       : {len(analysis_result.get('pasal_utama', []))} pasal")
            print(f"Total Duration    : {total_duration:.2f} seconds")
            print_separator()
            
            return {
                'success': True,
                'complaint_id': str(complaint_id),
                'complaint_number': complaint_number,
                'analysis_id': str(analysis_id),
                'duration_seconds': total_duration
            }
            
        except Exception as e:
            print(f"\n✗ Error during processing: {e}")
            import traceback
            traceback.print_exc()
            
            # Coba log error ke DB jika complaint_id sudah ada
            try:
                if complaint_id:
                    self.db.update_complaint_status(complaint_id, 'error')
                    self.db.log_action(
                        complaint_id=complaint_id,
                        analysis_id=analysis_id,
                        action='PROCESSING_ERROR',
                        action_by='system',
                        details=str(e)
                    )
            except Exception as db_e:
                print(f"✗ Failed to log processing error to DB: {db_e}")
                
            return {'success': False, 'error': str(e)}

# Bagian ini HANYA akan berjalan jika Anda menjalankan `python main.py`
# Bagian ini TIDAK akan berjalan saat diimpor oleh `api_server.py`
if __name__ == "__main__":
    """Main entry point for CLI execution"""
    
    # Check if PDF path is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_pdf>")
        print("Example: python main.py ./contoh_laporan_pengaduan.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Initialize processor
    try:
        processor = LegalComplaintProcessor()
        
        # Process complaint
        result = processor.process_complaint(pdf_path, uploaded_by='admin-cli')
        
        if result['success']:
            print(f"\n✅ Processing successful!")
            print(f"Complaint Number: {result['complaint_number']}")
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"FATAL: Gagal menginisialisasi LegalComplaintProcessor. Cek .env. Error: {e}")
        sys.exit(1)