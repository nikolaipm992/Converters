import os
from pdf2docx import Converter

# Фиксированный путь к папке Converters
folder_path = r'D:\Converters'

# Проверяем существование папки
if not os.path.exists(folder_path):
    print(f"❌ Папка {folder_path} не существует!")
    input("Нажмите Enter для выхода...")
    exit()

print(f"🔍 Поиск PDF-файлов в папке: {folder_path}")
pdf_count = 0

# Перебираем все файлы в папке D:\Converters
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        # Путь к PDF
        pdf_path = os.path.join(folder_path, filename)
        
        # Создаём имя для Word-файла
        word_filename = filename[:-4] + ".docx"
        word_path = os.path.join(folder_path, word_filename)

        print(f"\n🔄 Конвертирую: {filename} -> {word_filename}")
        pdf_count += 1

        try:
            # Конвертируем PDF в DOCX
            cv = Converter(pdf_path)
            cv.convert(word_path, start=0, end=None)
            cv.close()
            print(f"✅ Успешно сохранён: {word_filename}")
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")

if pdf_count == 0:
    print("❌ В папке D:\\Converters не найдено PDF-файлов для конвертации.")
else:
    print(f"\n🎉 Конвертация завершена! Обработано PDF-файлов: {pdf_count}")

input("\nНажмите Enter для выхода...")