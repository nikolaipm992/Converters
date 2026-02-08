import winreg

def unregister_context_menu():
    try:
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\\shell\\Конвертировать файл\\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\\shell\\Конвертировать файл")
        print("❌ Контекстное меню удалено из реестра.")
    except FileNotFoundError:
        print("❌ Пункт в реестре не найден.")

if __name__ == "__main__":
    unregister_context_menu()