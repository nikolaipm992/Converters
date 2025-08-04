import pandas as pd
import re
import os

# Регулярное выражение для email
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

# Фиксированный путь к папке Converters
folder_path = r'D:\Converters'
output_file = os.path.join(folder_path, 'emails.txt')

# Проверяем существование папки
if not os.path.exists(folder_path):
    print(f"❌ Папка {folder_path} не существует!")
    input("Нажмите Enter для выхода...")
    exit()

# Поиск всех Excel-файлов (.xls и .xlsx) в папке D:\Converters
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xls') or f.endswith('.xlsx')]

if not excel_files:
    print("❌ В папке D:\\Converters не найдено файлов Excel (.xls или .xlsx)")
else:
    print(f"✅ Найдено {len(excel_files)} Excel-файлов. Начинаем обработку...\n")

all_emails = []  # список для хранения всех email

# Обрабатываем каждый файл
for file in excel_files:
    file_path = os.path.join(folder_path, file)
    print(f"📄 Обработка файла: {file}")

    try:
        if file.endswith('.xlsx'):
            # Используем openpyxl для .xlsx
            df_dict = pd.read_excel(file_path, engine='openpyxl', sheet_name=None)
        elif file.endswith('.xls'):
            # Используем xlrd для .xls
            df_dict = pd.read_excel(file_path, engine='xlrd', sheet_name=None)

        # Перебираем все листы
        for sheet_name, sheet_df in df_dict.items():
            print(f"  🔍 Лист: {sheet_name}")
            for col in sheet_df.columns:
                for cell in sheet_df[col]:
                    if isinstance(cell, str):
                        emails_in_cell = re.findall(EMAIL_REGEX, cell)
                        all_emails.extend(emails_in_cell)
    except Exception as e:
        print(f"⚠️ Ошибка при обработке файла {file}: {e}")

# Подсчёт статистики
total_emails = len(all_emails)
unique_emails = list(set(all_emails))
duplicate_count = total_emails - len(unique_emails)

# Сохраняем уникальные email в файл в папке D:\Converters
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for email in unique_emails:
            f.write(email + '\n')
    print(f"\n✨ Всего найдено email'ов: {total_emails}")
    print(f"🔁 Найдено дубликатов: {duplicate_count}")
    print(f"✅ Уникальных email'ов: {len(unique_emails)}")
    print(f"📂 Уникальные email'ы сохранены в файл: {output_file}")
except Exception as e:
    print(f"❌ Не удалось сохранить файл: {e}")

input("\nНажмите Enter для выхода...")