import fitz  # PyMuPDF
import os

# Получаем текущую папку
current_dir = os.path.dirname(os.path.abspath(__file__))

# Собираем все изображения JPG в папке
image_files = [f for f in os.listdir(current_dir) if f.lower().endswith((".jpg", ".jpeg"))]
image_files.sort()  # Опционально: сортировка файлов по имени

if not image_files:
    print("В папке нет JPG-файлов для конвертации.")
else:
    for image_file in image_files:
        image_path = os.path.join(current_dir, image_file)
        pdf_path = os.path.join(current_dir, f"{os.path.splitext(image_file)[0]}.pdf")
        print(f"Конвертируется: {image_file}")

        doc = fitz.open()
        img_doc = fitz.open(image_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_doc.close()

        pdf_doc = fitz.open("pdf", pdf_bytes)
        doc.insert_pdf(pdf_doc)
        doc.save(pdf_path)
        doc.close()

        print(f"Сохранено: {pdf_path}")