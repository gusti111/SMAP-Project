from pypdf import PdfReader, PdfWriter
import os
import shutil
from pathlib import Path
from utils.logger import setup_logger

# Inisialisasi logger
logger = setup_logger()

class DocEngine:
    def compress(self, file_path, mode='lossy', output_dir=None):
        """
        Kompresi dokumen PDF dengan dukungan direktori output kustom.
        """
        # Tentukan direktori simpan: jika output_dir diberikan, gunakan itu; 
        # jika tidak, kembali ke folder asal file
        save_dir = Path(output_dir) if output_dir else file_path.parent
        output_path = save_dir / f"{file_path.stem}_{mode}{file_path.suffix}"
        
        try:
            # Pastikan direktori output ada (opsional, jika ingin sistem buatkan folder otomatis)
            if not save_dir.exists():
                save_dir.mkdir(parents=True, exist_ok=True)

            # Saat ini fokus pada file PDF
            if file_path.suffix.lower() == '.pdf':
                
                if mode == 'lossless':
                    # Lossless: Menyalin file asli tanpa mengubah isi/metadata sedikitpun
                    shutil.copy2(file_path, output_path)
                    msg = f"Sukses LOSSLESS: {output_path.name} (File tersalin utuh)"
                    logger.info(msg)
                    return msg
                
                else:
                    # Lossy: Menghapus metadata untuk memperkecil ukuran
                    reader = PdfReader(file_path)
                    writer = PdfWriter()

                    # Salin semua halaman
                    for page in reader.pages:
                        writer.add_page(page)

                    # Menghapus metadata
                    writer.add_metadata({})
                    
                    # Simpan file baru
                    with open(output_path, "wb") as f:
                        writer.write(f)
                        
                    msg = f"Sukses LOSSY: {output_path.name} (Metadata dihapus)"
                    logger.info(msg)
                    return msg
            
            else:
                warn_msg = f"Info: Optimasi untuk {file_path.suffix} belum diimplementasikan."
                logger.warning(warn_msg)
                return warn_msg
                
        except Exception as e:
            error_msg = f"Error Doc: {str(e)}"
            logger.error(error_msg)
            return error_msg
