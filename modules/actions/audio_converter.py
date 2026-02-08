import os
import json
import tkinter as tk
from tkinter import messagebox
from pydub import AudioSegment

class ConvertAudioWithPresetAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def convert_audio_with_preset(self):
        # Укажем, чтобы pydub использовал системный ffmpeg
        AudioSegment.converter = "ffmpeg"

        settings_path = os.path.join(os.path.dirname(__file__), "..", "..", "audio_settings.json")
        with open(settings_path, encoding="utf-8") as f:
            full_settings = json.load(f)

        presets = full_settings.get("presets", [])

        # Проверяем, является ли presets словарём или списком
        if isinstance(presets, dict):
            # Старый формат: {"preset_name": {...}}
            preset_options = {name: data for name, data in presets.items()}
        elif isinstance(presets, list):
            # Новый формат: [{"name": "...", ...}]
            preset_options = {preset["name"]: preset for preset in presets}
        else:
            print("❌ Ошибка: 'presets' не является ни словарём, ни массивом")
            return

        if not preset_options:
            print("❌ Нет доступных пресетов.")
            return

        # Создаём новое окно для выбора пресета
        root = tk.Toplevel()
        root.title("Выберите пресет")
        root.geometry("300x200")

        preset_names = list(preset_options.keys())

        selected_preset_name = tk.StringVar(value=preset_names[0])

        for name in preset_names:
            tk.Radiobutton(root, text=name, variable=selected_preset_name, value=name).pack(anchor="w", padx=20, pady=5)

        def apply_preset():
            selected_preset = preset_options[selected_preset_name.get()]
            format_type = selected_preset["format"]
            bitrate = selected_preset.get("bitrate")
            frequency = selected_preset.get("frequency", 44100)

            # Проверим, поддерживает ли pydub этот формат
            supported_formats = ["mp3", "wav", "flv", "ogg", "wma", "aac"]  # можно расширить
            if format_type not in supported_formats:
                print(f"❌ Формат {format_type} не поддерживается.")
                messagebox.showerror("Ошибка", f"Формат {format_type} не поддерживается.")
                return

            try:
                audio = AudioSegment.from_file(self.filepath)
            except Exception as e:
                print(f"❌ Ошибка при открытии файла: {e}")
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
                return

            if frequency:
                audio = audio.set_frame_rate(frequency)

            output_path = os.path.join(self.dir, f"{self.base}_converted.{format_type}")

            try:
                if bitrate:
                    audio.export(output_path, format=format_type, bitrate=bitrate)
                else:
                    audio.export(output_path, format=format_type)
                print(f"✅ Аудио сконвертировано: {output_path}")
                messagebox.showinfo("✅ Готово", "Аудио сконвертировано!")
            except Exception as e:
                print(f"❌ Ошибка при экспорте: {e}")
                messagebox.showerror("Ошибка", f"Не удалось экспортировать файл: {e}")

            root.destroy()

        tk.Button(root, text="Применить", command=apply_preset).pack(pady=10)

        root.mainloop()