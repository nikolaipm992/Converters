import fitz  # PyMuPDF
import os

# Фиксированный путь к папке Converters
folder_path = r'D:\Converters'

# Проверяем существование папки
if not os.path.exists(folder_path):
    print(f"❌ Папка {folder_path} не существует!")
    input("Нажмите Enter для выхода...")
    exit()

print(f"🔍 Поиск PDF-файлов в папке: {folder_path}")
pdf_count = 0

# Перебираем все PDF в папке
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(folder_path, filename)
        print(f"\n🔄 Конвертируется: {filename}")
        pdf_count += 1

        try:
            doc = fitz.open(pdf_path)
            pages_converted = 0
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)  # Можно менять качество через dpi
                output_filename = f"{os.path.splitext(filename)[0]}_стр_{page_num + 1}.jpg"
                output_path = os.path.join(folder_path, output_filename)
                pix.save(output_path, "jpeg")
                print(f"✅ Сохранено: {output_filename}")
                pages_converted += 1
                
            doc.close()
            print(f"✨ Страниц сконвертировано: {pages_converted}")
            
        except Exception as e:
            print(f"❌ Ошибка при конвертации {filename}: {e}")

if pdf_count == 0:
    print("❌ В папке D:\\Converters не найдено PDF-файлов для конвертации.")
else:
    print(f"\n🎉 Конвертация завершена! Обработано PDF-файлов: {pdf_count}")

input("\nНажмите Enter для выхода...")