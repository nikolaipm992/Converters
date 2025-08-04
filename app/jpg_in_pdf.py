import fitz  # PyMuPDF
import os

# Фиксированный путь к папке Converters
folder_path = r'D:\Converters'

# Проверяем существование папки
if not os.path.exists(folder_path):
    print(f"❌ Папка {folder_path} не существует!")
    input("Нажмите Enter для выхода...")
    exit()

# Собираем все изображения JPG в папке D:\Converters
image_files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg"))]
image_files.sort()  # Сортировка файлов по имени

if not image_files:
    print("❌ В папке D:\\Converters нет JPG-файлов для конвертации.")
else:
    print(f"✅ Найдено {len(image_files)} JPG-файлов для конвертации.\n")
    
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        pdf_path = os.path.join(folder_path, f"{os.path.splitext(image_file)[0]}.pdf")
        print(f"🔄 Конвертируется: {image_file}")

        try:
            doc = fitz.open()
            img_doc = fitz.open(image_path)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()

            pdf_doc = fitz.open("pdf", pdf_bytes)
            doc.insert_pdf(pdf_doc)
            doc.save(pdf_path)
            doc.close()

            print(f"✅ Сохранено: {pdf_path}")
        except Exception as e:
            print(f"❌ Ошибка при конвертации {image_file}: {e}")

    print(f"\n✨ Конвертация завершена! Обработано {len(image_files)} файлов.")

input("\nНажмите Enter для выхода...")