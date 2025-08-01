import os
from pdf2docx import Converter

# Получаем текущую директорию
current_dir = os.getcwd()

# Перебираем все файлы в текущей директории
for filename in os.listdir(current_dir):
    if filename.lower().endswith(".pdf"):
        # Путь к PDF
        pdf_path = os.path.join(current_dir, filename)
        
        # Создаём имя для Word-файла
        word_filename = filename[:-4] + ".docx"
        word_path = os.path.join(current_dir, word_filename)

        print(f"Конвертирую: {pdf_path} -> {word_path}")

        try:
            # Конвертируем PDF в DOCX
            cv = Converter(pdf_path)
            cv.convert(word_path, start=0, end=None)
            cv.close()
            print(f"✅ Успешно сохранён: {word_filename}")
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")

print("Конвертация завершена.")