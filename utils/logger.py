import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name="SMAP_Logger", log_file="app.log"):
    """
    Setup logger dengan RotatingFileHandler untuk mencegah file log membengkak.
    """
    logger = logging.getLogger(name)
    
    # Hindari duplikasi handler jika setup_logger dipanggil berkali-kali
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # RotatingFileHandler: Maksimal 5MB per file, simpan 3 file cadangan (backup)
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Console Handler agar log juga muncul di terminal untuk debugging
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger