import os
from tkinter import filedialog
from PyPDF2 import PdfMerger

class MergePdfsAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def merge_pdfs(self):
        files = filedialog.askopenfilenames(title="Выберите PDF-файлы для объединения", filetypes=[("PDF", "*.pdf")])
        if not files:
            print("❌ Нет выбранных файлов.")
            return

        merger = PdfMerger()

        for pdf in files:
            merger.append(pdf)

        output_path = os.path.join(self.dir, f"merged_{len(files)}_files.pdf")
        merger.write(output_path)
        merger.close()
        print(f"✅ PDF объединены: {output_path}")