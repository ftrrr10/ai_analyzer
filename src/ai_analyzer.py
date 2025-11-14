"""
AI Analysis Module
Handles AI-powered analysis of complaint documents using Gemini API
"""
import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class LegalAIAnalyzer:
    """AI-powered legal document analyzer using Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: Gemini API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.system_instruction = """
Anda adalah AI Legal Assistant bernama "LegalAnalyzer" yang ahli dalam menganalisis laporan pengaduan berdasarkan sistem hukum Indonesia.

TUGAS UTAMA:
1. Mengekstrak informasi penting dari laporan pengaduan
2. Mengidentifikasi pasal-pasal hukum Indonesia yang relevan (KUHP, KUHAP, UU ITE, dll)
3. Memberikan ringkasan dan rekomendasi tindak lanjut

PRINSIP KERJA:
✓ Objektif dan berbasis fakta
✓ Gunakan Bahasa Indonesia formal
✓ Sertakan confidence score untuk setiap rekomendasi
✓ Transparan tentang keterbatasan

BATASAN:
⚠️ Hanya memberikan REKOMENDASI, bukan keputusan hukum final
⚠️ Output harus divalidasi oleh ahli hukum
⚠️ Tidak membuat informasi palsu (no hallucination)

OUTPUT: Harus berupa VALID JSON tanpa markdown formatting.
"""
    
    def create_analysis_prompt(self, document_text: str) -> str:
        """Create structured prompt for analysis"""
        
        prompt = f"""
{self.system_instruction}

Analisis laporan pengaduan berikut dan berikan output dalam format JSON:

═══════════════════════════════════════════════════════════════
DOKUMEN LAPORAN PENGADUAN:
═══════════════════════════════════════════════════════════════

{document_text}

═══════════════════════════════════════════════════════════════
OUTPUT FORMAT (HARUS VALID JSON):
═══════════════════════════════════════════════════════════════

{{
  "pelapor": {{
    "nama": "",
    "ktp": "",
    "kontak": ""
  }},
  "terlapor": {{
    "nama": "",
    "identitas": "",
    "ciri": ""
  }},
  "kejadian": {{
    "tanggal": "YYYY-MM-DD",
    "waktu": "HH:MM",
    "lokasi": "",
    "provinsi": ""
  }},
  "kronologi": "",
  "jenis_kasus": "",
  "kerugian": {{
    "materil": 0.0,
    "immateril": ""
  }},
  "bukti": {{
    "fisik": [],
    "dokumen": [],
    "saksi": [],
    "digital": []
  }},
  "pasal_utama": [
    {{
      "pasal_number": "",
      "sumber_hukum": "",
      "judul_pasal": "",
      "bunyi_pasal": "",
      "elemen_konstitutif": [],
      "elemen_terpenuhi": [
        {{
          "elemen": "",
          "fakta_pendukung": "",
          "status": "terpenuhi"
        }}
      ],
      "confidence_score": 0.0,
      "confidence_level": "Tinggi",
      "reasoning": "",
      "is_primary": true,
      "article_type": "utama"
    }}
  ],
  "pasal_alternatif": [],
  "summary": {{
    "executive_summary": "",
    "key_points": [],
    "tingkat_urgensi": "Sedang",
    "alasan_urgensi": "",
    "missing_information": []
  }},
  "quality": {{
    "kelengkapan_laporan": "Lengkap",  // MUST be: "Lengkap", "Tidak Lengkap", or "Parsial"
    "kualitas_bukti": "Kuat",          // MUST be: "Kuat", "Sedang", or "Lemah"
    "kompleksitas_kasus": "Sedang"     // MUST be: "Tinggi", "Sedang", or "Rendah"
  }},
  "recommendations": [
    {{
      "text": "",
      "priority": "Normal",
      "category": ""
    }}
  ]
}}

PENTING:
- Response harus VALID JSON tanpa markdown code blocks (```
- Semua field harus terisi, gunakan null atau [] jika tidak ada data
- confidence_score harus float antara 0.0 - 1.0
- Tanggal format: YYYY-MM-DD
- Waktu format: HH:MM
- kelengkapan_laporan HARUS salah satu dari: "Lengkap", "Tidak Lengkap", "Parsial"
- kualitas_bukti HARUS salah satu dari: "Kuat", "Sedang", "Lemah"
- kompleksitas_kasus HARUS salah satu dari: "Tinggi", "Sedang", "Rendah"
- tingkat_urgensi HARUS salah satu dari: "Tinggi", "Sedang", "Rendah"
"""
        return prompt
    
    def analyze(self, document_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze complaint document
        
        Args:
            document_text: Extracted text from PDF
            
        Returns:
            Analysis result as dictionary or None if failed
        """
        print("\n🤖 Starting AI analysis...")
        start_time = time.time()
        
        try:
            # Create prompt
            prompt = self.create_analysis_prompt(document_text)
            
            # Call Gemini API
            print("  → Calling Gemini API...")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Low for consistency
                    max_output_tokens=4000,
                    top_p=0.9,
                )
            )
            
            # Parse response
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])  # Remove first and last line
                if result_text.startswith('json'):
                    result_text = result_text[4:].strip()
            
            # Parse JSON
            analysis_result = json.loads(result_text)
            
            # Calculate duration
            duration = int(time.time() - start_time)
            analysis_result['_metadata'] = {
                'analysis_duration_seconds': duration,
                'analyzed_at': datetime.now().isoformat(),
                'model': 'gemini-1.5-pro-latest'
            }
            
            print(f"  ✓ Analysis completed in {duration} seconds")
            return analysis_result
            
        except json.JSONDecodeError as e:
            print(f"  ✗ Error parsing JSON response: {e}")
            print(f"  Response text: {result_text[:500]}...")
            return None
            
        except Exception as e:
            print(f"  ✗ Error during analysis: {e}")
            return None
    
    def validate_analysis(self, analysis: Dict[str, Any]) -> bool:
        """
        Validate analysis result structure
        
        Args:
            analysis: Analysis result dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = ['pelapor', 'terlapor', 'kejadian', 'jenis_kasus', 'pasal_utama', 'summary']
        
        for key in required_keys:
            if key not in analysis:
                print(f"  ⚠ Missing required key: {key}")
                return False
        
        return True
