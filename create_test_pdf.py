"""
Create a simple test PDF for legal complaint analyzer
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf():
    filename = "contoh_laporan_pengaduan.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "FORMULIR LAPORAN PENGADUAN")
    
    # Add content
    c.setFont("Helvetica", 12)
    y = 700
    
    content = [
        "Nomor Laporan: ADU-2025-001847",
        "Tanggal Laporan: 11 November 2025",
        "",
        "DATA PELAPOR:",
        "Nama Lengkap: Budi Santoso",
        "Nomor Identitas (KTP): 3174001234567890",
        "Pekerjaan: Karyawan Swasta",
        "Alamat: Jl. Gatot Subroto No. 45, Jakarta Pusat",
        "No. Telepon: 0812-3456-7890",
        "",
        "DATA TERLAPOR:",
        "Nama: Tidak Diketahui",
        "Ciri-ciri: Tinggi ~170 cm, Tato ular di lengan kanan",
        "",
        "KRONOLOGI KEJADIAN:",
        "Tanggal: 10 November 2025, Pukul 15.30 WIB",
        "Lokasi: Stasiun Gambir, Jakarta Pusat",
        "",
        "Saya sedang menunggu kereta api di Stasiun Gambir.",
        "Saya meletakkan dompet berisi uang Rp 2.500.000",
        "dan identitas diri di tas kerja saya.",
        "Sekitar pukul 15.35, saya melihat seorang laki-laki",
        "mengambil dompet saya dari dalam tas.",
        "Saya langsung berteriak namun pelaku berlari.",
        "",
        "Rekaman CCTV menunjukkan pelaku mengambil dompet saya.",
        "Ada transaksi mencurigakan di kartu kredit saya",
        "sebesar Rp 3.500.000 setelah kejadian.",
        "",
        "BUKTI:",
        "- Rekaman CCTV Stasiun Gambir",
        "- Laporan transaksi kartu kredit",
        "- Keterangan Petugas Keamanan",
        "",
        "PERMINTAAN:",
        "Mohon melakukan penyelidikan dan menangkap pelaku."
    ]
    
    for line in content:
        c.drawString(100, y, line)
        y -= 20
        if y < 50:  # New page if needed
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    
    c.save()
    print(f"✓ PDF created: {filename}")

if __name__ == "__main__":
    try:
        create_test_pdf()
    except ImportError:
        print("⚠ reportlab not installed. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        create_test_pdf()
