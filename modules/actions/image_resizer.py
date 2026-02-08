import os
from tkinter import simpledialog
from PIL import Image

class ResizeImageAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def resize_image(self):
        # Открываем диалог для ввода ширины и высоты
        from tkinter import Tk
        root = Tk()
        root.withdraw()  # прячем главное окно

        width = simpledialog.askinteger("Ширина", "Введите ширину:", initialvalue=1024)
        height = simpledialog.askinteger("Высота", "Введите высоту:", initialvalue=768)

        if width and height:
            img = Image.open(self.filepath)
            resized_img = img.resize((width, height))
            output_path = os.path.join(self.dir, f"{self.base}_resized{self.ext}")
            resized_img.save(output_path)
            print(f"✅ Изображение изменено: {output_path}")
        else:
            print("❌ Размеры не указаны.")