import winreg
import os
import sys

def register_context_menu():
    script_path = os.path.abspath("run.py")
    command = f'"{sys.executable}" "{script_path}" "%1"'

    key_path = r"*\\shell\\Конвертировать файл"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
        winreg.SetValue(key, "", winreg.REG_SZ, "Конвертировать файл")

    subkey_path = key_path + r"\\command"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, subkey_path) as key:
        winreg.SetValue(key, "", winreg.REG_SZ, command)

if __name__ == "__main__":
    register_context_menu()
    print("✅ Контекстное меню успешно зарегистрировано.")