import os
from docx2pdf import convert

def convert_docx_folder(folder_path):
    """Конвертирует все .docx файлы в папке в PDF"""
    print(f"🔍 Ищу .docx файлы в папке: {folder_path}")
    
    # Проверяем существование папки
    if not os.path.exists(folder_path):
        print(f"❌ Папка {folder_path} не существует!")
        return False
    
    # Ищем все .docx файлы в папке
    docx_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.docx')]
    
    if not docx_files:
        print("❌ В папке не найдено .docx файлов для конвертации.")
        return False
    
    print(f"✅ Найдено {len(docx_files)} файлов для конвертации:")
    for file in docx_files:
        print(f"   - {file}")
    
    try:
        # Конвертируем все файлы в той же папке
        convert(folder_path, folder_path)
        print("✅ Конвертация завершена успешно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        return False

if __name__ == "__main__":
    # Фиксированный путь к папке Converters
    folder_path = r'D:\Converters'
    
    print("🚀 Конвертация Word в PDF")
    print("=" * 40)
    
    success = convert_docx_folder(folder_path)
    
    if success:
        print(f"\n📁 Сконвертированные файлы сохранены в папке: {folder_path}")
    else:
        print(f"\n⚠️  Конвертация не удалась. Проверьте папку {folder_path}")
    
    input("\nНажмите Enter для выхода...")