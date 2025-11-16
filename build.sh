#!/bin/bash

# Skrip ini akan dijalankan oleh Vercel SEBELUM build Python
# Tujuannya untuk menginstal dependensi sistem (bukan Python)

echo "BUILD_SCRIPT: Memulai instalasi dependensi sistem..."

# 1. Update package list
#    Set DEBIAN_FRONTEND=noninteractive untuk menghindari prompt
export DEBIAN_FRONTEND=noninteractive
apt-get update

# 2. Instal Tesseract (diperlukan oleh pytesseract)
#    -y = otomatis yes
echo "BUILD_SCRIPT: Menginstal tesseract-ocr dan bahasa Indonesia..."
apt-get install -y tesseract-ocr tesseract-ocr-ind

# 3. Instal Poppler (diperlukan oleh pdf2image)
echo "BUILD_SCRIPT: Menginstal poppler-utils..."
apt-get install -y poppler-utils

# 4. (Opsional) Bersihkan cache apt untuk mengurangi ukuran
apt-get clean

echo "BUILD_SCRIPT: Instalasi dependensi sistem selesai."

# 5. Buat output dummy untuk static build
#    Build @vercel/static-build HARUS menghasilkan folder 'public'
mkdir -p public
echo "Dependensi sistem telah diinstal oleh build.sh." > public/index.html