# -*- coding: utf-8 -*-
import os
import sys
from PyPDF2 import PdfMerger

def merge_pdfs_in_parent_folder():
    """Объединяет все PDF-файлы в родительской папке (на уровень выше) в один файл"""
    
    # Получаем путь к папке на уровень выше (где находится bat-файл)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_dir)
    
    print(f"Рабочая папка: {parent_folder}")
    
    try:
        merger = PdfMerger()
    except Exception as e:
        print(f"Ошибка при создании PdfMerger: {e}")
        input("Нажмите Enter для продолжения...")
        return

    # Получаем список всех PDF-файлов в родительской папке
    try:
        pdf_files = []
        for f in os.listdir(parent_folder):
            if f.lower().endswith('.pdf'):
                pdf_files.append(f)
        pdf_files.sort()  # Сортировка по имени файла
    except Exception as e:
        print(f"Ошибка при чтении папки: {e}")
        input("Нажмите Enter для продолжения...")
        return

    if not pdf_files:
        print("В папке не найдено PDF-файлов!")
        input("Нажмите Enter для возврата в меню...")
        return

    print(f"Найдено {len(pdf_files)} PDF-файлов:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf}")

    print("\nОбъединяю файлы...")
    
    success_count = 0
    for pdf in pdf_files:
        pdf_path = os.path.join(parent_folder, pdf)
        try:
            print(f"  Добавляю: {pdf}")
            merger.append(open(pdf_path, 'rb'))
            success_count += 1
        except Exception as e:
            print(f"  Ошибка при добавлении {pdf}: {e}")

    if success_count == 0:
        print("Не удалось добавить ни один файл!")
        merger.close()
        input("Нажмите Enter для возврата в меню...")
        return

    # Имя выходного файла (в той же папке)
    output_filename = 'объединённый_файл.pdf'
    output_path = os.path.join(parent_folder, output_filename)
    
    # Записываем объединённый PDF
    try:
        print(f"\nСохраняю результат в: {output_filename}")
        with open(output_path, 'wb') as output_file:
            merger.write(output_file)
        merger.close()
        print(f"Готово! Файл сохранен как: {output_filename}")
        print(f"Объединено файлов: {success_count}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        merger.close()

    input("\nНажмите Enter для возврата в меню...")

# Запускаем функцию
if __name__ == "__main__":
    try:
        merge_pdfs_in_parent_folder()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для завершения...")