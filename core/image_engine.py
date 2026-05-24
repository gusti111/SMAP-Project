from PIL import Image
import os
from pathlib import Path
from utils.logger import setup_logger
from utils.ssim_validator import get_ssim_score

# Inisialisasi logger
logger = setup_logger()

class ImageEngine:
    def compress(self, file_path, mode='lossy', output_dir=None):
        """
        Kompresi gambar dengan dukungan direktori output kustom.
        """
        # Tentukan direktori simpan: jika output_dir diberikan, gunakan itu; 
        # jika tidak, kembali ke folder asal file
        save_dir = Path(output_dir) if output_dir else file_path.parent
        
        # Pastikan direktori output ada
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Menentukan output path berdasarkan mode
        if mode == 'lossless':
            output_path = save_dir / f"{file_path.stem}_lossless{file_path.suffix}"
        else:
            output_path = save_dir / f"{file_path.stem}_compressed.webp"
        
        # Penentuan method kompresi:
        # Lossless = 6 (kualitas maksimal/presisi)
        # Lossy = 3 (keseimbangan kecepatan dan ukuran)
        method = 6 if mode == 'lossless' else 3
        
        try:
            logger.info(f"Memulai kompresi: {file_path.name} (Mode: {mode}, Method: {method})")
            
            with Image.open(file_path) as img:
                if mode == 'lossless':
                    # Optimasi tanpa kehilangan data
                    img.save(output_path, img.format, optimize=True)
                else:
                    # Optimasi High Quality WebP
                    img.save(
                        output_path, 
                        'WEBP', 
                        quality=92, 
                        method=method, 
                        exact=True
                    )
            
            # Kalkulasi efisiensi
            original_size = os.path.getsize(file_path)
            new_size = os.path.getsize(output_path)
            reduction = ((original_size - new_size) / original_size) * 100
            
            # Validasi Kualitas dengan SSIM
            # Semakin mendekati 1.0, semakin mirip dengan aslinya
            score = get_ssim_score(file_path, output_path)
            
            msg = f"Sukses {mode.upper()}: {output_path.name} (Reduksi: {reduction:.1f}%, SSIM: {score})"
            logger.info(msg)
            return msg
            
        except Exception as e:
            error_msg = f"Error Image: {str(e)}"
            logger.error(error_msg)
            return error_msg