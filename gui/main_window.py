import subprocess
import re
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, 
                               QTextEdit, QProgressBar, QDialog, QRadioButton, 
                               QDialogButtonBox, QPushButton, QHBoxLayout, QFileDialog)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QThread, Signal
from core.dispatcher import Dispatcher
from core.video_engine import VideoEngine

# Dialog untuk memilih mode berdasarkan konteks file
class CompressionDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.path = Path(file_path)
        ext = self.path.suffix.lower()
        self.setWindowTitle("Pilih Mode Kompresi")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"File: {self.path.name}"))
        
        # Logika adaptif
        if ext in ['.mp4', '.mkv', '.mov', '.avi']:
            self.radio1 = QRadioButton("Balanced (x265 - High Quality)\nKeseimbangan durasi & ukuran.")
            self.radio2 = QRadioButton("Speed (Ultrafast - Low Latency)\nProses encoding cepat, ukuran lebih besar.")
            self.mode_map = {'opt1': 'balanced', 'opt2': 'speed'}
        elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
            self.radio1 = QRadioButton("Lossless (Original)\nKualitas 100%, ukuran besar.")
            self.radio2 = QRadioButton("Lossy (WebP HQ)\nKualitas visual 95%, lebih optimal.")
            self.mode_map = {'opt1': 'lossless', 'opt2': 'lossy'}
        else:
            self.radio1 = QRadioButton("Original (Copy)\nMenyalin file asli.")
            self.radio2 = QRadioButton("Clean Metadata (Optimized)\nHapus info sensitif.")
            self.mode_map = {'opt1': 'lossless', 'opt2': 'lossy'}

        self.radio1.setChecked(True)
        layout.addWidget(self.radio1)
        layout.addWidget(self.radio2)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_mode(self):
        return self.mode_map['opt1'] if self.radio1.isChecked() else self.mode_map['opt2']

class CompressionWorker(QThread):
    progress_updated = Signal(int)
    finished = Signal(str)

    def __init__(self, file_path, dispatcher, mode, output_dir=None):
        super().__init__()
        self.file_path = file_path
        self.dispatcher = dispatcher
        self.mode = mode
        self.output_dir = output_dir
        self.video_engine = VideoEngine()

    def run(self):
        try:
            path_obj = Path(self.file_path)
            ext = path_obj.suffix.lower()
            
            # Tentukan direktori simpan: default ke folder asli jika output_dir tidak diset
            save_dir = Path(self.output_dir) if self.output_dir else path_obj.parent
            output_path = save_dir / f"{path_obj.stem}_compressed{path_obj.suffix}"
            
            if ext in ['.mp4', '.mkv', '.mov', '.avi']:
                # --- LOGIKA VIDEO ---
                total_duration = self.video_engine.get_duration(path_obj)
                preset = 'faster' if self.mode == 'balanced' else 'ultrafast'
                
                cmd = [self.video_engine.ffmpeg_path, '-i', str(path_obj),
                       '-vcodec', 'libx265', '-preset', preset, '-crf', '28',
                       '-y', str(output_path)]
                
                process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
                
                while True:
                    line = process.stderr.readline()
                    if not line: break
                    time_match = re.search(r"time=(\d+):(\d+):(\d+)", line)
                    if time_match and total_duration > 0:
                        h, m, s = map(int, time_match.groups())
                        pct = int(((h * 3600 + m * 60 + s) / total_duration) * 100)
                        self.progress_updated.emit(min(pct, 100))
                self.finished.emit(f"Sukses ({self.mode}): {output_path.name}")
            else:
                # --- LOGIKA NON-VIDEO ---
                # PERBAIKAN: Sekarang meneruskan output_dir ke dispatcher
                result = self.dispatcher.dispatch(str(path_obj), self.mode, output_dir=self.output_dir)
                self.progress_updated.emit(100)
                self.finished.emit(result)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

class DropArea(QLabel):
    def __init__(self):
        super().__init__("Drag & Drop File di Sini")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; border-radius: 10px; padding: 20px; background-color: #f9f9f9;")
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files: self.window().start_compression(files[0])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMAP - Smart Media Adaptive Processor")
        # --- Tambahkan kode ini untuk set icon ---
        icon_path = Path("assets/logo.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        # ----------------------------------------
        self.setMinimumSize(500, 450)
        self.dispatcher = Dispatcher()
        self.output_dir = None
        
        layout = QVBoxLayout()
        
        # Kontrol File & Output
        ctrl_layout = QHBoxLayout()
        self.btn_browse = QPushButton("Pilih File")
        self.btn_browse.clicked.connect(self.browse_file)
        self.btn_folder = QPushButton("Folder Output")
        self.btn_folder.clicked.connect(self.select_output_folder)
        ctrl_layout.addWidget(self.btn_browse)
        ctrl_layout.addWidget(self.btn_folder)
        layout.addLayout(ctrl_layout)
        
        self.lbl_output = QLabel("Output: Default (Sama dengan asal)")
        layout.addWidget(self.lbl_output)
        
        self.drop_area = DropArea()
        self.progress_bar = QProgressBar()
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        
        layout.addWidget(self.drop_area)
        layout.addWidget(QLabel("Progress:"))
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Status Log:"))
        layout.addWidget(self.status_log)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Media")
        if file_path:
            self.start_compression(file_path)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Penyimpanan")
        if folder:
            self.output_dir = folder
            self.lbl_output.setText(f"Output: {folder}")

    def start_compression(self, file_path):
        dialog = CompressionDialog(file_path)
        if dialog.exec():
            mode = dialog.get_mode()
            self.status_log.append(f"Memproses: {Path(file_path).name} [Mode: {mode}]")
            
            # UX: Indeterminate progress untuk non-video
            ext = Path(file_path).suffix.lower()
            self.progress_bar.setRange(0, 0) if ext not in ['.mp4', '.mkv', '.mov', '.avi'] else self.progress_bar.setRange(0, 100)
            
            self.worker = CompressionWorker(file_path, self.dispatcher, mode, self.output_dir)
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.on_finished)
            self.worker.start()

    def on_finished(self, result):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.status_log.append(result)
