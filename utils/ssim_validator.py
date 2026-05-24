import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image

def get_ssim_score(original_path, compressed_path):
    """
    Menghitung skor SSIM antara dua gambar.
    Skor berkisar antara -1 (sangat berbeda) hingga 1 (identik).
    """
    try:
        # Load gambar dan pastikan dalam mode RGB
        img_orig = Image.open(original_path).convert('RGB')
        img_comp = Image.open(compressed_path).convert('RGB')

        # SSIM membutuhkan dimensi yang sama
        if img_orig.size != img_comp.size:
            # Jika berbeda, resize compressed ke original untuk validasi
            img_comp = img_comp.resize(img_orig.size, Image.Resampling.LANCZOS)

        # Ubah ke numpy array
        arr_orig = np.array(img_orig)
        arr_comp = np.array(img_comp)

        # Hitung SSIM
        # channel_axis=2 menandakan gambar memiliki 3 channel (RGB)
        score = ssim(arr_orig, arr_comp, channel_axis=2, data_range=255)
        
        return round(score, 4)
        
    except Exception as e:
        print(f"Gagal menghitung SSIM: {e}")
        return 0.0