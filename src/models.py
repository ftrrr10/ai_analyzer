"""
Data Models for Legal Complaint Analyzer
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field
from uuid import UUID

class Complaint(BaseModel):
    """Complaint data model"""
    id: Optional[UUID] = None
    complaint_number: str
    upload_date: Optional[datetime] = None
    pdf_filename: str
    pdf_path: Optional[str] = None
    pdf_url: Optional[str] = None
    extracted_text: Optional[str] = None
    status: str = 'pending'
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LegalArticle(BaseModel):
    """Legal article recommendation model"""
    id: Optional[UUID] = None
    analysis_id: Optional[UUID] = None
    pasal_number: str
    sumber_hukum: str
    judul_pasal: Optional[str] = None
    bunyi_pasal: Optional[str] = None
    elemen_konstitutif: Optional[List[str]] = None
    elemen_terpenuhi: Optional[List[Dict[str, Any]]] = None
    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_level: str
    reasoning: Optional[str] = None
    is_primary: bool = False
    article_type: str = 'utama'

class AnalysisResult(BaseModel):
    """Analysis result data model"""
    id: Optional[UUID] = None
    complaint_id: UUID
    
    # Pelapor
    pelapor_nama: Optional[str] = None
    pelapor_ktp: Optional[str] = None
    pelapor_kontak: Optional[str] = None
    
    # Terlapor
    terlapor_nama: Optional[str] = None
    terlapor_identitas: Optional[str] = None
    terlapor_ciri: Optional[str] = None
    
    # Kejadian
    kejadian_tanggal: Optional[date] = None
    kejadian_waktu: Optional[time] = None
    kejadian_lokasi: Optional[str] = None
    kejadian_provinsi: Optional[str] = None
    
    # Kasus
    kronologi: Optional[str] = None
    jenis_kasus: Optional[str] = None
    
    # Kerugian
    kerugian_materil: Optional[float] = None
    kerugian_immateril: Optional[str] = None
    
    # Bukti
    bukti_fisik: Optional[List[str]] = None
    bukti_dokumen: Optional[List[str]] = None
    bukti_saksi: Optional[List[str]] = None
    bukti_digital: Optional[List[str]] = None
    
    # Summary
    executive_summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    tingkat_urgensi: Optional[str] = None
    alasan_urgensi: Optional[str] = None
    missing_information: Optional[List[str]] = None
    
    # Quality
    kelengkapan_laporan: Optional[str] = None
    kualitas_bukti: Optional[str] = None
    kompleksitas_kasus: Optional[str] = None
    
    # Metadata
    full_analysis_json: Optional[Dict[str, Any]] = None
    analyzed_by: Optional[str] = None
    analysis_duration_seconds: Optional[int] = None
    created_at: Optional[datetime] = None

class Recommendation(BaseModel):
    """Recommendation model"""
    id: Optional[UUID] = None
    analysis_id: UUID
    recommendation_text: str
    priority: str = 'Normal'
    category: Optional[str] = None
    status: str = 'pending'
    assigned_to: Optional[str] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
