import os
import whisper

class AudioToTextWhisperAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def audio_to_text_whisper(self):
        print(f"DEBUG: Начинаем обработку файла: {self.filepath}")
        print(f"DEBUG: Директория: {self.dir}")
        print(f"DEBUG: Имя файла: {self.base}")
        print(f"DEBUG: Расширение: {self.ext}")

        try:
            print("DEBUG: Загружаем модель Whisper...")
            model = whisper.load_model("small")
            print("DEBUG: Модель загружена. Начинаем транскрибацию...")
            result = model.transcribe(self.filepath, language="Russian")
            print("DEBUG: Транскрибация завершена.")
            text = result["text"]

            print(f"DEBUG: Текст: {text[:100]}...")  # Показываем первые 100 символов

            # Сохраняем в TXT
            output_path = os.path.join(self.dir, f"{self.base}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            print(f"✅ Текст из аудио сохранён: {output_path}")
        except Exception as e:
            print(f"❌ Ошибка при распознавании: {e}")
            print(f"DEBUG: Пытаемся создать файл с ошибкой...")
            output_path = os.path.join(self.dir, f"{self.base}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Ошибка при распознавании: {e}")
            print(f"✅ Файл с ошибкой создан: {output_path}")