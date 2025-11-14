"""
Database Operations Module
Handles all interactions with Supabase database
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from config.database_config import supabase
from src.models import Complaint, AnalysisResult, LegalArticle, Recommendation


class DatabaseManager:
    """Manages all database operations for the Legal Complaint Analyzer"""
    
    def __init__(self):
        self.client = supabase
    
    # ═══════════════════════════════════════════════════════════
    # COMPLAINTS OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def create_complaint(self, complaint: Complaint) -> Dict[str, Any]:
        """
        Create a new complaint record
        
        Args:
            complaint: Complaint model instance
            
        Returns:
            Created complaint data with ID
        """
        try:
            data = {
                'complaint_number': complaint.complaint_number,
                'pdf_filename': complaint.pdf_filename,
                'pdf_path': complaint.pdf_path,
                'pdf_url': complaint.pdf_url,
                'extracted_text': complaint.extracted_text,
                'status': complaint.status,
                'uploaded_by': complaint.uploaded_by
            }
            
            response = self.client.table('complaints').insert(data).execute()
            print(f"✓ Complaint created with ID: {response.data[0]['id']}")
            return response.data[0]
            
        except Exception as e:
            print(f"✗ Error creating complaint: {e}")
            raise
    
    def get_complaint_by_id(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Get complaint by ID"""
        try:
            response = self.client.table('complaints').select("*").eq('id', complaint_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"✗ Error getting complaint: {e}")
            return None
    
    def get_complaint_by_number(self, complaint_number: str) -> Optional[Dict[str, Any]]:
        """Get complaint by complaint number"""
        try:
            response = self.client.table('complaints').select("*").eq('complaint_number', complaint_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"✗ Error getting complaint: {e}")
            return None
    
    def update_complaint_status(self, complaint_id: str, status: str) -> bool:
        """Update complaint status"""
        try:
            self.client.table('complaints').update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', complaint_id).execute()
            print(f"✓ Complaint status updated to: {status}")
            return True
        except Exception as e:
            print(f"✗ Error updating complaint status: {e}")
            return False
    
    def get_all_complaints(self, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all complaints with optional status filter"""
        try:
            query = self.client.table('complaints').select("*").order('upload_date', desc=True).limit(limit)
            
            if status:
                query = query.eq('status', status)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"✗ Error getting complaints: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════
    # ANALYSIS RESULTS OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def create_analysis_result(self, analysis: AnalysisResult) -> Dict[str, Any]:
        """Create analysis result record"""
        try:
            data = {
                'complaint_id': str(analysis.complaint_id),
                'pelapor_nama': analysis.pelapor_nama,
                'pelapor_ktp': analysis.pelapor_ktp,
                'pelapor_kontak': analysis.pelapor_kontak,
                'terlapor_nama': analysis.terlapor_nama,
                'terlapor_identitas': analysis.terlapor_identitas,
                'terlapor_ciri': analysis.terlapor_ciri,
                'kejadian_tanggal': analysis.kejadian_tanggal.isoformat() if analysis.kejadian_tanggal else None,
                'kejadian_waktu': analysis.kejadian_waktu.isoformat() if analysis.kejadian_waktu else None,
                'kejadian_lokasi': analysis.kejadian_lokasi,
                'kejadian_provinsi': analysis.kejadian_provinsi,
                'kronologi': analysis.kronologi,
                'jenis_kasus': analysis.jenis_kasus,
                'kerugian_materil': analysis.kerugian_materil,
                'kerugian_immateril': analysis.kerugian_immateril,
                'bukti_fisik': analysis.bukti_fisik,
                'bukti_dokumen': analysis.bukti_dokumen,
                'bukti_saksi': analysis.bukti_saksi,
                'bukti_digital': analysis.bukti_digital,
                'executive_summary': analysis.executive_summary,
                'key_points': analysis.key_points,
                'tingkat_urgensi': analysis.tingkat_urgensi,
                'alasan_urgensi': analysis.alasan_urgensi,
                'missing_information': analysis.missing_information,
                'kelengkapan_laporan': analysis.kelengkapan_laporan,
                'kualitas_bukti': analysis.kualitas_bukti,
                'kompleksitas_kasus': analysis.kompleksitas_kasus,
                'full_analysis_json': analysis.full_analysis_json,
                'analyzed_by': analysis.analyzed_by,
                'analysis_duration_seconds': analysis.analysis_duration_seconds
            }
            
            response = self.client.table('analysis_results').insert(data).execute()
            print(f"✓ Analysis result created with ID: {response.data[0]['id']}")
            return response.data[0]
            
        except Exception as e:
            print(f"✗ Error creating analysis result: {e}")
            raise
    
    def get_analysis_by_complaint_id(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result by complaint ID"""
        try:
            response = self.client.table('analysis_results').select("*").eq('complaint_id', complaint_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"✗ Error getting analysis: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════
    # LEGAL ARTICLES OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def create_legal_article(self, article: LegalArticle) -> Dict[str, Any]:
        """Create legal article recommendation"""
        try:
            data = {
                'analysis_id': str(article.analysis_id),
                'pasal_number': article.pasal_number,
                'sumber_hukum': article.sumber_hukum,
                'judul_pasal': article.judul_pasal,
                'bunyi_pasal': article.bunyi_pasal,
                'elemen_konstitutif': article.elemen_konstitutif,
                'elemen_terpenuhi': article.elemen_terpenuhi,
                'confidence_score': article.confidence_score,
                'confidence_level': article.confidence_level,
                'reasoning': article.reasoning,
                'is_primary': article.is_primary,
                'article_type': article.article_type
            }
            
            response = self.client.table('legal_articles').insert(data).execute()
            return response.data[0]
            
        except Exception as e:
            print(f"✗ Error creating legal article: {e}")
            raise
    
    def get_articles_by_analysis_id(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get all legal articles for an analysis"""
        try:
            response = self.client.table('legal_articles').select("*").eq('analysis_id', analysis_id).order('confidence_score', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"✗ Error getting legal articles: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════
    # RECOMMENDATIONS OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def create_recommendation(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Create recommendation record"""
        try:
            data = {
                'analysis_id': str(recommendation.analysis_id),
                'recommendation_text': recommendation.recommendation_text,
                'priority': recommendation.priority,
                'category': recommendation.category,
                'status': recommendation.status,
                'assigned_to': recommendation.assigned_to,
                'notes': recommendation.notes
            }
            
            response = self.client.table('recommendations').insert(data).execute()
            return response.data[0]
            
        except Exception as e:
            print(f"✗ Error creating recommendation: {e}")
            raise
    
    def get_recommendations_by_analysis_id(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Get all recommendations for an analysis"""
        try:
            response = self.client.table('recommendations').select("*").eq('analysis_id', analysis_id).execute()
            return response.data
        except Exception as e:
            print(f"✗ Error getting recommendations: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════
    # AUDIT LOGS OPERATIONS
    # ═══════════════════════════════════════════════════════════
    
    def log_action(self, complaint_id: Optional[str], analysis_id: Optional[str], 
                   action: str, action_by: str, details: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create audit log entry"""
        try:
            data = {
                'complaint_id': complaint_id,
                'analysis_id': analysis_id,
                'action': action,
                'action_by': action_by,
                'details': details,
                'metadata': metadata
            }
            
            self.client.table('analysis_logs').insert(data).execute()
            return True
            
        except Exception as e:
            print(f"✗ Error creating log: {e}")
            return False
    
    def get_logs_by_complaint_id(self, complaint_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get audit logs for a complaint"""
        try:
            response = self.client.table('analysis_logs').select("*").eq('complaint_id', complaint_id).order('timestamp', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"✗ Error getting logs: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════
    # COMPLEX QUERIES & VIEWS
    # ═══════════════════════════════════════════════════════════
    
    def get_complaint_with_analysis(self, complaint_id: str) -> Optional[Dict[str, Any]]:
        """Get complete complaint data with analysis and articles"""
        try:
            # Get complaint
            complaint = self.get_complaint_by_id(complaint_id)
            if not complaint:
                return None
            
            # Get analysis
            analysis = self.get_analysis_by_complaint_id(complaint_id)
            
            # Get legal articles if analysis exists
            articles = []
            recommendations = []
            if analysis:
                articles = self.get_articles_by_analysis_id(analysis['id'])
                recommendations = self.get_recommendations_by_analysis_id(analysis['id'])
            
            # Combine all data
            result = {
                'complaint': complaint,
                'analysis': analysis,
                'legal_articles': articles,
                'recommendations': recommendations
            }
            
            return result
            
        except Exception as e:
            print(f"✗ Error getting complete complaint data: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            # Total complaints
            total_complaints = self.client.table('complaints').select("*", count='exact').execute()
            
            # By status
            pending = self.client.table('complaints').select("*", count='exact').eq('status', 'pending').execute()
            analyzed = self.client.table('complaints').select("*", count='exact').eq('status', 'analyzed').execute()
            
            # By urgency
            high_urgency = self.client.table('analysis_results').select("*", count='exact').eq('tingkat_urgensi', 'Tinggi').execute()
            
            stats = {
                'total_complaints': total_complaints.count,
                'pending': pending.count,
                'analyzed': analyzed.count,
                'high_urgency': high_urgency.count
            }
            
            return stats
            
        except Exception as e:
            print(f"✗ Error getting statistics: {e}")
            return {}
