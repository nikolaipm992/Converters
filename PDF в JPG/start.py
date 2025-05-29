import fitz  # PyMuPDF
import os

# Получаем текущую папку
current_dir = os.path.dirname(os.path.abspath(__file__))

# Перебираем все PDF в папке
for filename in os.listdir(current_dir):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(current_dir, filename)
        print(f"Конвертируется: {filename}")

        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)  # Можно менять качество через dpi
            output_filename = f"{os.path.splitext(filename)[0]}_стр_{page_num + 1}.jpg"
            output_path = os.path.join(current_dir, output_filename)
            pix.save(output_path, "jpeg")
            print(f"Сохранено: {output_filename}")
        doc.close()