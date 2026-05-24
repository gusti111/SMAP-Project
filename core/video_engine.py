import ffmpeg
import os
from pathlib import Path
from utils.logger import setup_logger

# Inisialisasi logger
logger = setup_logger()

class VideoEngine:
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.ffmpeg_path = os.path.join(base_path, "..", "bin", "ffmpeg.exe")
        self.ffprobe_path = os.path.join(base_path, "..", "bin", "ffprobe.exe")

    def get_duration(self, file_path):
        """Membaca durasi video dengan logging yang jelas."""
        if not os.path.exists(self.ffprobe_path):
            logger.warning(f"ffprobe.exe tidak ditemukan di {self.ffprobe_path}")
            return 0
            
        try:
            probe = ffmpeg.probe(str(file_path), cmd=self.ffprobe_path)
            format_info = probe.get('format', {})
            duration = format_info.get('duration')
            return float(duration) if duration else 0
        except Exception as e:
            logger.error(f"Gagal membaca durasi {file_path.name}: {e}")
            return 0

    def compress(self, file_path, mode='balanced', output_dir=None):
        """
        Kompresi video dengan preset dinamis dan dukungan output_dir.
        """
        # Tentukan direktori simpan
        save_dir = Path(output_dir) if output_dir else file_path.parent
        
        # Pastikan direktori output ada
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)
            
        output_path = save_dir / f"{file_path.stem}_compressed{file_path.suffix}"
        
        if not os.path.exists(self.ffmpeg_path):
            error_msg = f"ffmpeg.exe tidak ditemukan di {self.ffmpeg_path}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

        # Mapping mode ke preset FFmpeg
        preset = 'faster' if mode == 'balanced' else 'ultrafast'
        logger.info(f"Memulai kompresi video: {file_path.name} [Preset: {preset}, Output: {save_dir}]")

        try:
            (
                ffmpeg
                .input(str(file_path))
                .output(
                    str(output_path), 
                    vcodec='libx265', 
                    preset=preset, 
                    crf=28, 
                    y=None # overwrite output
                )
                .run(cmd=self.ffmpeg_path, overwrite_output=True)
            )
            
            msg = f"Sukses ({mode}): {output_path.name}"
            logger.info(msg)
            return msg
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Error Video {file_path.name}: {error_msg}")
            return f"Error Video: {error_msg}"