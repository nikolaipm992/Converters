import os
from docx import Document
import pytesseract
from PIL import Image
import io
import time
import sys

# Глобальные флаги доступности
TESSERACT_AVAILABLE = False
PIL_AVAILABLE = False

# Попробуем импортировать необходимые библиотеки
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("✓ PIL (Pillow) доступен")
except ImportError:
    PIL_AVAILABLE = False
    print("✗ PIL (Pillow) не найден")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✓ Tesseract OCR доступен")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("✗ Tesseract OCR не найден")

def process_single_image(image_data, image_index):
    """Обработка одного изображения"""
    if not PIL_AVAILABLE or not TESSERACT_AVAILABLE:
        return image_index, ""
    
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Настройки для ускорения Tesseract
        custom_config = r'--oem 1 --psm 6 -c tessedit_do_invert=0'
        text = pytesseract.image_to_string(image, lang='rus+eng', config=custom_config)
        
        if text.strip():
            return image_index, text.strip()
        return image_index, ""
    except Exception as e:
        print(f"    Ошибка обработки изображения {image_index}: {str(e)[:50]}...")
        return image_index, ""

def extract_text_and_images(docx_path):
    """Извлекает текст и изображения последовательно"""
    if not PIL_AVAILABLE:
        print("  PIL не доступен - обрабатываю только текст")
    
    try:
        doc = Document(docx_path)
        text_parts = []
        images_data = []
        
        print(f"  Читаю документ...")
        
        # Извлекаем текст
        for i, paragraph in enumerate(doc.paragraphs):
            if paragraph.text.strip():
                text_parts.append(('text', paragraph.text))
        
        # Собираем данные изображений (если PIL доступен)
        if PIL_AVAILABLE and TESSERACT_AVAILABLE:
            for i, rel in enumerate(doc.part.rels.values()):
                if "image" in rel.target_ref:
                    try:
                        image_part = rel.target_part
                        image_bytes = image_part.blob
                        images_data.append((image_bytes, i + 1))
                    except Exception as e:
                        print(f"    Ошибка чтения изображения {i + 1}: {e}")
            
            print(f"  Найдено изображений: {len(images_data)}")
            
            # Последовательная обработка изображений
            if images_data:
                image_texts = {}
                
                for img_data, img_index in images_data:
                    result_index, text = process_single_image(img_data, img_index)
                    if text:
                        image_texts[result_index] = text
                        print(f"    ✓ Обработано изображение {result_index} ({len(text)} символов)")
                
                # Добавляем текст из изображений в порядке их следования
                for img_data, img_index in images_data:
                    if img_index in image_texts and image_texts[img_index]:
                        text_parts.append(('image', f"[Изображение {img_index}]\n{image_texts[img_index]}\n"))
            elif images_data:
                print("  OCR недоступен - изображения пропущены")
        
        return text_parts
        
    except Exception as e:
        print(f"  Ошибка обработки файла {docx_path}: {e}")
        return []

def process_document_file(filename, folder_path):
    """Обработка одного документа"""
    file_path = os.path.join(folder_path, filename)
    print(f"📄 Обрабатываю: {filename}")
    
    start_time = time.time()
    text_parts = extract_text_and_images(file_path)
    end_time = time.time()
    
    print(f"  ⏱️  {filename} обработан за {end_time - start_time:.2f} секунд")
    return filename, text_parts

def main():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(folder_path, "результат.txt")
    
    print("ОБЪЕДИНЕНИЕ ВСЕХ ДОКУМЕНТОВ")
    print("="*60)
    print(f"Папка: {folder_path}")
    print("="*60)
    
    # Находим все .docx файлы
    docx_files = [f for f in os.listdir(folder_path) if f.endswith('.docx') and f != os.path.basename(__file__)]
    
    if not docx_files:
        print("❌ Не найдено .docx файлов в папке")
        return
    
    print(f"🔍 Найдено документов: {len(docx_files)}")
    
    start_time = time.time()
    
    # Собираем весь текст последовательно
    all_text_parts = []
    
    # Обрабатываем документы последовательно
    for filename in docx_files:
        filename, text_parts = process_document_file(filename, folder_path)
        all_text_parts.extend(text_parts)
    
    end_time = time.time()
    
    # Создаем сплошной текст
    final_text_parts = []
    for item_type, text in all_text_parts:
        final_text_parts.append(text)
    
    final_text = '\n'.join(final_text_parts)
    
    # Сохраняем результат
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ОБЪЕДИНЕННЫЙ ТЕКСТ ВСЕХ ДОКУМЕНТОВ\n")
            f.write("="*60 + "\n\n")
            f.write(final_text)
                
        print(f"\n✅ Готово! Результат сохранен в: {output_file}")
        print(f"📊 Общее количество частей: {len(all_text_parts)}")
        print(f"📊 Общий объем текста: {len(final_text)} символов")
        print(f"⏱️  Общее время обработки: {end_time - start_time:.2f} секунд")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

if __name__ == "__main__":
    # Увеличиваем лимит рекурсии если нужно
    sys.setrecursionlimit(10000)
    main()