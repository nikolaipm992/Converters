import os
import fitz  # PyMuPDF

class PdfToImageAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def pdf_to_image(self):
        doc = fitz.open(self.filepath)
        page = doc[0]
        pix = page.get_pixmap()
        output_path = os.path.join(self.dir, f"{self.base}.png")
        pix.save(output_path)
        print(f"✅ PDF сохранён как изображение: {output_path}")