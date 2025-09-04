import ffmpeg
import os
import sys
from pathlib import Path
import subprocess

def remux_audio(input_file, output_file, audio_codec='aac', audio_bitrate='320k', sample_rate=48000, channels=2):
    """Изменяет аудио кодек в видео файле без перекодирования видео"""
    try:
        if not os.path.exists(input_file):
            return {"success": False, "error": f"Файл не найден: {input_file}"}
            
        # Создаем папку для выходного файла если её нет
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Параметры аудио
        audio_args = {
            'acodec': audio_codec,
            'b:a': audio_bitrate,
            'ar': sample_rate,
            'ac': channels
        }
        
        # Для некоторых кодеков убираем битрейт
        if audio_codec in ['copy', 'flac']:
            audio_args.pop('b:a', None)
        
        # Путь к ffmpeg
        ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
        
        # Получаем информацию о видео потоке для копирования без перекодирования
        probe = ffmpeg.probe(input_file, cmd=ffmpeg_exe.replace('ffmpeg.exe', 'ffprobe.exe'))
        
        # Определяем видео кодек (пытаемся скопировать без перекодирования)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        video_codec = 'copy' if video_stream else None
        
        # Команда ffmpeg - копируем видео, перекодируем только аудио
        if video_codec:
            (
                ffmpeg
                .input(input_file)
                .output(output_file, vcodec=video_codec, **audio_args)
                .overwrite_output()
                .global_args('-y')
                .global_args('-hide_banner')
                .global_args('-loglevel', 'error')
                .run(cmd=ffmpeg_exe)
            )
        else:
            # Если видео поток не найден, перекодируем всё
            (
                ffmpeg
                .input(input_file)
                .output(output_file, **audio_args)
                .overwrite_output()
                .global_args('-y')
                .global_args('-hide_banner')
                .global_args('-loglevel', 'error')
                .run(cmd=ffmpeg_exe)
            )
        
        return {"success": True, "error": None}
        
    except ffmpeg.Error as e:
        error_msg = f"FFmpeg ошибка: {e.stderr.decode() if e.stderr else str(e)}"
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Общая ошибка: {str(e)}"
        return {"success": False, "error": error_msg}

def find_video_files(directory):
    """Поиск видео файлов в директории"""
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
    video_files = []
    path = Path(directory)
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in video_extensions:
            video_files.append(str(file))
    return video_files

def main():
    # Путь к папке с видео файлами
    folder_path = r'D:\Converters'
    
    # Проверяем существование папки
    if not os.path.exists(folder_path):
        print(f"❌ Папка {folder_path} не существует!")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    # Проверяем ffmpeg
    ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
    ffprobe_exe = r"D:\codecs\ffmpeg\ffprobe.exe"
    
    if not os.path.exists(ffmpeg_exe):
        print(f"❌ FFmpeg не найден по пути: {ffmpeg_exe}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    if not os.path.exists(ffprobe_exe):
        print(f"❌ FFprobe не найден по пути: {ffprobe_exe}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    print("🎵 Аудио Ремуксер (изменение аудио кодека в видео)")
    print("=" * 50)
    print(f"Папка: {folder_path}")
    
    # Ищем видео файлы
    video_files = find_video_files(folder_path)
    
    if not video_files:
        print("❌ Не найдено видео файлов для обработки")
        input("Нажмите Enter для выхода...")
        return
    
    print(f"Найдено файлов: {len(video_files)}")
    for file in video_files:
        print(f"   - {Path(file).name}")
    
    # Выбор аудио кодека
    print("\nВыберите аудио кодек:")
    print("1. AAC (по умолчанию, хорошее качество)")
    print("2. MP3 (совместимость)")
    print("3. AC3 (Dolby Digital)")
    print("4. EAC3 (Dolby Digital Plus)")
    print("5. FLAC (без потерь)")
    print("6. Копировать оригинальный аудио поток (без изменений)")
    
    codec_choice = input("Введите номер (1-6) или Enter для AAC: ").strip()
    codec_map = {
        "1": ("aac", "320k"),
        "2": ("mp3", "320k"),
        "3": ("ac3", "640k"),
        "4": ("eac3", "640k"),
        "5": ("flac", " Lossless"),
        "6": ("copy", "copy")
    }
    
    audio_codec, default_bitrate = codec_map.get(codec_choice, ("aac", "320k"))
    
    # Если выбрано копирование, пропускаем настройку битрейта
    if audio_codec == "copy":
        audio_bitrate = "copy"
        sample_rate = 0  # Не меняем
        channels = 0     # Не меняем
    else:
        # Выбор битрейта
        if audio_codec not in ['flac']:
            print(f"\nВыберите битрейт для {audio_codec.upper()}:")
            bitrate_options = {
                "aac": ["64k", "128k", "192k", "256k", "320k"],
                "mp3": ["64k", "128k", "192k", "256k", "320k"],
                "ac3": ["192k", "384k", "448k", "640k"],
                "eac3": ["192k", "384k", "448k", "640k"]
            }
            
            bitrates = bitrate_options.get(audio_codec, ["128k", "192k", "256k", "320k"])
            
            for i, br in enumerate(bitrates, 1):
                marker = " (рекомендуется)" if br == default_bitrate.replace(" Lossless", "") else ""
                print(f"{i}. {br}{marker}")
            
            bitrate_choice = input(f"Введите номер (1-{len(bitrates)}) или Enter для {default_bitrate}: ").strip()
            
            if bitrate_choice.isdigit() and 1 <= int(bitrate_choice) <= len(bitrates):
                audio_bitrate = bitrates[int(bitrate_choice) - 1]
            else:
                audio_bitrate = default_bitrate.replace(" Lossless", "")
        else:
            audio_bitrate = None  # Для FLAC не нужен битрейт
        
        # Частота дискретизации
        print(f"\nЧастота дискретизации (Гц):")
        print("1. 22050 Гц")
        print("2. 44100 Гц (CD качество)")
        print("3. 48000 Гц (по умолчанию)")
        print("4. 96000 Гц (высокое качество)")
        
        sample_rate_choice = input("Введите номер (1-4) или Enter для 48000: ").strip()
        sample_rate_map = {"1": 22050, "2": 44100, "3": 48000, "4": 96000}
        sample_rate = sample_rate_map.get(sample_rate_choice, 48000)
        
        # Количество каналов
        print(f"\nКоличество аудио каналов:")
        print("1. 1 (моно)")
        print("2. 2 (стерео, по умолчанию)")
        print("3. 6 (5.1 surround)")
        
        channels_choice = input("Введите номер (1-3) или Enter для стерео: ").strip()
        channels_map = {"1": 1, "2": 2, "3": 6}
        channels = channels_map.get(channels_choice, 2)
    
    # Подтверждение
    print(f"\nНастройки:")
    if audio_codec == "copy":
        print(f"  Кодек: Копирование оригинального аудио")
    else:
        print(f"  Кодек: {audio_codec.upper()}")
        if audio_bitrate:
            print(f"  Битрейт: {audio_bitrate}")
        print(f"  Частота: {sample_rate} Гц")
        print(f"  Каналы: {channels}")
    
    confirm = input("\nПродолжить? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', 'д', 'да', '']:
        print("Отменено пользователем")
        input("Нажмите Enter для выхода...")
        return
    
    print(f"\nНачинаем изменение аудио кодека...")
    
    # Обрабатываем каждый файл
    for i, video_file in enumerate(video_files, 1):
        input_path = Path(video_file)
        output_filename = f"{input_path.stem}_audio_remuxed{input_path.suffix}"
        output_file = os.path.join(folder_path, output_filename)
        
        # Проверяем, существует ли уже такой файл
        counter = 1
        while os.path.exists(output_file):
            output_filename = f"{input_path.stem}_audio_remuxed_{counter}{input_path.suffix}"
            output_file = os.path.join(folder_path, output_filename)
            counter += 1
        
        print(f"[{i}/{len(video_files)}] Обработка: {input_path.name} → {output_filename}")
        
        # Параметры для функции
        kwargs = {'audio_codec': audio_codec}
        if audio_codec != "copy":
            if audio_bitrate:
                kwargs['audio_bitrate'] = audio_bitrate
            kwargs['sample_rate'] = sample_rate
            kwargs['channels'] = channels
        else:
            kwargs['audio_bitrate'] = 'copy'
        
        result = remux_audio(video_file, output_file, **kwargs)
        
        if result["success"]:
            print(f"✅ Успешно сохранено: {output_filename}")
        else:
            print(f"❌ Ошибка: {result['error']}")
    
    print(f"\n🎉 Обработка завершена! Файлы сохранены в папке: {folder_path}")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()