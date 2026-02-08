import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

venv_site_packages = os.path.join(os.path.dirname(__file__), "venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

def log_error(error_msg):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(script_dir, "error.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[ERROR] {error_msg}\n")

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, encoding='utf-8') as f:
        return json.load(f)

def main():
    try:
        if len(sys.argv) < 2:
            log_error("Не указан файл.")
            messagebox.showerror("Ошибка", "Файл не передан.")
            return

        filepath = sys.argv[1]

        config = load_config()
        actions = config['actions']

        root = tk.Tk()
        root.title("Конвертер файлов")
        root.geometry("400x300")

        label = tk.Label(root, text=f"Файл: {filepath}")
        label.pack(pady=10)

        listbox = tk.Listbox(root, height=len(actions), width=70)
        for action in actions:
            listbox.insert(tk.END, action['display'])
        listbox.pack(pady=10)

        def execute_action():
            index = listbox.curselection()
            if index:
                selected = actions[index[0]]
                module_name = selected['module']
                function_name = selected['function']

                # Импортируем модуль
                module = __import__(f"modules.{module_name}", fromlist=[function_name])

                # Получаем класс (предполагаем, что имя класса совпадает с именем функции + Action)
                class_name = ''.join(word.capitalize() for word in function_name.split('_')) + "Action"
                action_class = getattr(module, class_name)
                action_instance = action_class(filepath)

                # Вызываем метод
                getattr(action_instance, function_name)()

                messagebox.showinfo("✅ Готово", "Действие выполнено.")
                root.destroy()

        button = tk.Button(root, text="Выполнить", command=execute_action)
        button.pack(pady=10)

        root.mainloop()
    except Exception as e:
        error_msg = str(e)
        log_error(error_msg)
        messagebox.showerror("Ошибка", f"Произошла ошибка: {error_msg}")

if __name__ == "__main__":
    main()