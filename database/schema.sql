-- ═══════════════════════════════════════════════════════════════
-- LEGAL COMPLAINT ANALYZER - DATABASE SCHEMA
-- Database: PostgreSQL (Supabase)
-- ═══════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: complaints
CREATE TABLE complaints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_number VARCHAR(50) UNIQUE NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_filename VARCHAR(255),
    pdf_path TEXT,
    pdf_url TEXT,
    extracted_text TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'analyzed', 'validated', 'error')),
    uploaded_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_upload_date ON complaints(upload_date DESC);
CREATE INDEX idx_complaints_number ON complaints(complaint_number);

-- Table: analysis_results
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id UUID NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    pelapor_nama VARCHAR(255),
    pelapor_ktp VARCHAR(50),
    pelapor_kontak VARCHAR(100),
    terlapor_nama VARCHAR(255),
    terlapor_identitas VARCHAR(255),
    terlapor_ciri TEXT,
    kejadian_tanggal DATE,
    kejadian_waktu TIME,
    kejadian_lokasi TEXT,
    kejadian_provinsi VARCHAR(100),
    kronologi TEXT,
    jenis_kasus VARCHAR(100),
    kerugian_materil NUMERIC(15,2),
    kerugian_immateril TEXT,
    bukti_fisik TEXT[],
    bukti_dokumen TEXT[],
    bukti_saksi TEXT[],
    bukti_digital TEXT[],
    executive_summary TEXT,
    key_points TEXT[],
    tingkat_urgensi VARCHAR(50) CHECK (tingkat_urgensi IN ('Tinggi', 'Sedang', 'Rendah', 'Cukup', 'Sangat Tinggi', 'Sangat Rendah', 'Kritis')),
    alasan_urgensi TEXT,
    missing_information TEXT[],
    kelengkapan_laporan VARCHAR(50) CHECK (kelengkapan_laporan IN ('Lengkap', 'Tidak Lengkap', 'Parsial', 'Cukup Lengkap', 'Sangat Lengkap')),
    kualitas_bukti VARCHAR(50) CHECK (kualitas_bukti IN ('Kuat', 'Sedang', 'Lemah', 'Cukup', 'Sangat Kuat', 'Sangat Lemah', 'Tidak Ada')),
    kompleksitas_kasus VARCHAR(50) CHECK (kompleksitas_kasus IN ('Tinggi', 'Sedang', 'Rendah', 'Sangat Tinggi', 'Sangat Rendah')),
    full_analysis_json JSONB,
    analyzed_by VARCHAR(100),
    analysis_duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id)
);

CREATE INDEX idx_analysis_complaint_id ON analysis_results(complaint_id);
CREATE INDEX idx_analysis_jenis_kasus ON analysis_results(jenis_kasus);
CREATE INDEX idx_analysis_urgensi ON analysis_results(tingkat_urgensi);
CREATE INDEX idx_analysis_tanggal ON analysis_results(kejadian_tanggal DESC);

-- Table: legal_articles
CREATE TABLE legal_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    pasal_number VARCHAR(50) NOT NULL,
    sumber_hukum VARCHAR(100) NOT NULL,
    judul_pasal VARCHAR(255),
    bunyi_pasal TEXT,
    elemen_konstitutif TEXT[],
    elemen_terpenuhi JSONB,
    confidence_score NUMERIC(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    confidence_level VARCHAR(50) CHECK (confidence_level IN ('Tinggi', 'Sedang', 'Rendah')),
    reasoning TEXT,
    is_primary BOOLEAN DEFAULT FALSE,
    article_type VARCHAR(50) CHECK (article_type IN ('utama', 'alternatif', 'pemberatan', 'terkait')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id)
);

CREATE INDEX idx_articles_analysis_id ON legal_articles(analysis_id);
CREATE INDEX idx_articles_pasal ON legal_articles(pasal_number);
CREATE INDEX idx_articles_confidence ON legal_articles(confidence_score DESC);
CREATE INDEX idx_articles_primary ON legal_articles(is_primary) WHERE is_primary = TRUE;

-- Table: recommendations
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    priority VARCHAR(50) CHECK (priority IN ('Urgent', 'Normal', 'Low')),
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'dismissed')),
    assigned_to VARCHAR(100),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id)
);

CREATE INDEX idx_recommendations_analysis ON recommendations(analysis_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);

-- Table: analysis_logs
CREATE TABLE analysis_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id UUID REFERENCES complaints(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    action_by VARCHAR(100),
    details TEXT,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_logs_complaint ON analysis_logs(complaint_id);
CREATE INDEX idx_logs_analysis ON analysis_logs(analysis_id);
CREATE INDEX idx_logs_timestamp ON analysis_logs(timestamp DESC);
CREATE INDEX idx_logs_action ON analysis_logs(action);

-- Table: users (optional)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('admin', 'analyst', 'validator', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_complaints_updated_at
    BEFORE UPDATE ON complaints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recommendations_updated_at
    BEFORE UPDATE ON recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
