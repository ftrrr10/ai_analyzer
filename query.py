-- ═══════════════════════════════════════════════════════════════
-- COMMON QUERIES FOR LEGAL COMPLAINT ANALYZER
-- ═══════════════════════════════════════════════════════════════

-- Query 1: Get all pending complaints
SELECT * FROM complaints 
WHERE status = 'pending' 
ORDER BY upload_date DESC;

-- Query 2: Get complaint with full analysis
SELECT 
    c.*,
    a.executive_summary,
    a.jenis_kasus,
    a.tingkat_urgensi,
    json_agg(la.*) as legal_articles
FROM complaints c
LEFT JOIN analysis_results a ON c.id = a.complaint_id
LEFT JOIN legal_articles la ON a.id = la.analysis_id
WHERE c.complaint_number = 'ADU-XXXXXXX'
GROUP BY c.id, a.id;

-- Query 3: Statistics - Cases by type
SELECT 
    jenis_kasus,
    COUNT(*) as total,
    AVG(confidence_score) as avg_confidence
FROM analysis_results a
JOIN legal_articles la ON a.id = la.analysis_id
WHERE la.is_primary = TRUE
GROUP BY jenis_kasus
ORDER BY total DESC;

-- Query 4: High urgency cases
SELECT * FROM v_complaint_summary
WHERE tingkat_urgensi = 'Tinggi'
AND status = 'analyzed'
ORDER BY upload_date DESC;

-- Query 5: Cases with incomplete information
SELECT 
    complaint_number,
    pelapor_nama,
    jenis_kasus,
    kelengkapan_laporan,
    missing_information
FROM complaints c
JOIN analysis_results a ON c.id = a.complaint_id
WHERE kelengkapan_laporan = 'Tidak Lengkap';

-- Query 6: Most common legal articles
SELECT 
    pasal_number,
    sumber_hukum,
    COUNT(*) as frequency,
    AVG(confidence_score) as avg_confidence
FROM legal_articles
WHERE is_primary = TRUE
GROUP BY pasal_number, sumber_hukum
ORDER BY frequency DESC
LIMIT 10;

-- Query 7: Analysis performance metrics
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_analyzed,
    AVG(analysis_duration_seconds) as avg_duration,
    MIN(analysis_duration_seconds) as min_duration,
    MAX(analysis_duration_seconds) as max_duration
FROM analysis_results
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Query 8: Audit trail for specific complaint
SELECT * FROM analysis_logs
WHERE complaint_id = 'uuid-here'
ORDER BY timestamp DESC;
