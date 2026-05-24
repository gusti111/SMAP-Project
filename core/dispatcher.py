from pathlib import Path
from core.video_engine import VideoEngine
from core.image_engine import ImageEngine
from core.doc_engine import DocEngine
from utils.logger import setup_logger

# Inisialisasi logger
logger = setup_logger()

class Dispatcher:
    def __init__(self):
        # Inisialisasi engine
        self.engines = {
            'video': VideoEngine(),
            'image': ImageEngine(),
            'doc': DocEngine()
        }
        
        # Mapping ekstensi ke jenis engine
        self.extension_map = {
            '.mp4': 'video', '.mkv': 'video', '.mov': 'video', '.avi': 'video',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.webp': 'image',
            '.pdf': 'doc', '.docx': 'doc'
        }

    def dispatch(self, file_path_str, mode='lossy', output_dir=None):
        """
        Mengklasifikasikan file dan mengarahkan ke engine yang tepat.
        Meneruskan parameter mode dan output_dir untuk fleksibilitas penyimpanan.
        """
        file_path = Path(file_path_str)
        ext = file_path.suffix.lower()
        
        if not file_path.exists():
            error_msg = f"Error: File {file_path} tidak ditemukan."
            logger.error(error_msg)
            return error_msg

        category = self.extension_map.get(ext)
        
        if category and category in self.engines:
            engine = self.engines[category]
            
            # Logging informatif
            dest = output_dir if output_dir else "folder asal"
            logger.info(f"Mengarahkan {file_path.name} ke {category}_engine (Mode: {mode}, Output: {dest})")
            
            # Meneruskan mode dan output_dir ke fungsi compress
            try:
                # Mencoba memanggil dengan semua parameter
                return engine.compress(file_path, mode=mode, output_dir=output_dir)
            except TypeError:
                # Fallback jika engine belum mendukung output_dir
                logger.warning(f"Engine {category} tidak mendukung semua parameter, mencoba versi lama.")
                try:
                    return engine.compress(file_path, mode=mode)
                except TypeError:
                    return engine.compress(file_path)
        
        error_msg = f"Error: Format file {ext} belum didukung oleh engine manapun."
        logger.error(error_msg)
        return error_msg

# Contoh penggunaan
if __name__ == "__main__":
    dispatcher = Dispatcher()
