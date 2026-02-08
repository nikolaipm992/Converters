import os
from PIL import Image

class ImageToPdfAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def image_to_pdf(self):
        img = Image.open(self.filepath)
        output_path = os.path.join(self.dir, f"{self.base}.pdf")
        img.save(output_path, "PDF", resolution=100.0)
        print(f"✅ Изображение сохранено в PDF: {output_path}")