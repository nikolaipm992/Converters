import os
import ffmpeg
from pathlib import Path

# Настройки конвертации
INPUT_FOLDER = "."  # текущая папка
OUTPUT_SUFFIX = "converted_"
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm'}

def convert_video(input_path, output_path):
    try:
        print(f"Конвертирую: {input_path} -> {output_path}")
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                vcodec='libx264',
                preset='fast',
                crf=23,
                acodec='aac',
                audio_bitrate='192k'
            )
            .run(overwrite_output=True)
        )
    except Exception as e:
        print(f"Ошибка при конвертации {input_path}: {e}")

def process_folder(root_dir):
    root_path = Path(root_dir).absolute()
    output_root = root_path.parent / (OUTPUT_SUFFIX + root_path.name)

    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = Path(dirpath).relative_to(root_path)
        output_dir = output_root / rel_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                output_file = output_dir / (file_path.stem + ".mp4")
                if not output_file.exists():
                    convert_video(str(file_path), str(output_file))
                else:
                    print(f"Пропускаю (уже существует): {output_file}")

if __name__ == "__main__":
    process_folder(INPUT_FOLDER)
    print("✅ Все файлы успешно обработаны!")