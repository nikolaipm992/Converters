import os
from docx2pdf import convert

def convert_docx_folder(folder_path):
    print(f"Ищу .docx файлы в папке: {folder_path}")
    convert(folder_path, folder_path)
    print("Конвертация завершена.")

if __name__ == "__main__":
    current_folder = os.getcwd()
    convert_docx_folder(current_folder)