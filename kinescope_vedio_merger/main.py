import os
import glob
import subprocess

def check_ffmpeg():
    """Проверяет наличие ffmpeg в системном PATH"""
    try:
        # Просто запускаем 'ffmpeg -version', он должен быть доступен в PATH
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        # Проверим, действительно ли это ffmpeg, а не другая команда
        if "ffmpeg version" in result.stdout:
            return True
        else:
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def find_video_audio_files():
    """Находит видео и аудио mp4 файлы"""
    mp4_files = glob.glob("*.mp4")
    
    if len(mp4_files) < 2:
        return None, None
    
    video_file = None
    audio_file = None
    
    # Пытаемся определить, какой файл видео, а какой аудио
    for file in mp4_files:
        # Ищем ключевые слова в названиях
        if any(keyword in file.lower() for keyword in ["video", "vid", "without", "noaudio", "silent"]):
            video_file = file
        elif any(keyword in file.lower() for keyword in ["audio", "sound", "music", "voice"]):
            audio_file = file
    
    # Если не определили по ключевым словам
    if not video_file and not audio_file and len(mp4_files) >= 2:
        # Берем первый как видео, второй как аудио
        video_file = mp4_files[0]
        audio_file = mp4_files[1]
    elif not video_file and audio_file and len(mp4_files) >= 2:
        # Нашли аудио, ищем видео
        for file in mp4_files:
            if file != audio_file:
                video_file = file
                break
    elif video_file and not audio_file and len(mp4_files) >= 2:
        # Нашли видео, ищем аудио
        for file in mp4_files:
            if file != video_file:
                audio_file = file
                break
    
    return video_file, audio_file

def merge_files(video_file, audio_file, output_file):
    """Объединяет видео и аудио файлы, используя ffmpeg из PATH"""
    # Используем 'ffmpeg' напрямую, предполагая, что он в PATH
    command = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "copy", # Также используем copy для аудио, если формат совместим
        "-y",
        output_file
    ]
    
    # Если copy для аудио не работает, попробуем перекодировать в aac
    command_fallback = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-y",
        output_file
    ]
    
    try:
        # Пробуем скопировать потоки без перекодировки
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return True, "Успешно объединено!"
        else:
            # Пробуем с перекодировкой аудио
            print("Попытка перекодировки аудио...")
            result = subprocess.run(command_fallback, capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Успешно объединено с перекодировкой аудио!"
            else:
                return False, f"Ошибка ffmpeg: {result.stderr}"
    except Exception as e:
        return False, f"Ошибка запуска ffmpeg: {str(e)}"

def main():
    print("🎥 Объединение двух MP4 файлов (видео + аудио)")
    print("=" * 50)
    
    # Проверяем наличие ffmpeg в системном PATH
    if not check_ffmpeg():
        print("❌ FFmpeg не найден в системном PATH!")
        print("Пожалуйста, убедитесь, что FFmpeg установлен и путь к нему добавлен в переменную среды PATH.")
        print("Скачать FFmpeg и инструкции по установке можно здесь: https://ffmpeg.org/download.html")
        input("\nНажмите Enter для выхода...")
        return
    
    print("✅ FFmpeg найден в системе.")
    
    # Показываем все mp4 файлы
    mp4_files = glob.glob("*.mp4")
    print(f"Найдено {len(mp4_files)} MP4 файлов:")
    for i, file in enumerate(mp4_files, 1):
        size_mb = os.path.getsize(file) / (1024 * 1024)
        print(f"  {i}. {file} ({size_mb:.1f} MB)")
    print()
    
    if len(mp4_files) < 2:
        print("❌ Нужно минимум 2 файла .mp4")
        input("\nНажмите Enter для выхода...")
        return
    
    # Определяем видео и аудио файлы
    video_file, audio_file = find_video_audio_files()
    
    if not video_file or not audio_file:
        # Если не смогли автоматически определить, спрашиваем у пользователя
        print("Не удалось автоматически определить, какой файл видео, а какой аудио.")
        print("Пожалуйста, выберите файлы вручную:")
        
        for i, file in enumerate(mp4_files, 1):
            print(f"  {i}. {file}")
        
        try:
            video_choice = int(input("\nВведите номер файла с видео: ")) - 1
            audio_choice = int(input("Введите номер файла с аудио: ")) - 1
            
            if 0 <= video_choice < len(mp4_files) and 0 <= audio_choice < len(mp4_files) and video_choice != audio_choice:
                video_file = mp4_files[video_choice]
                audio_file = mp4_files[audio_choice]
            else:
                print("❌ Неверный выбор!")
                input("\nНажмите Enter для выхода...")
                return
        except ValueError:
            print("❌ Неверный ввод!")
            input("\nНажмите Enter для выхода...")
            return
    
    print(f"🎬 Файл видео: {video_file}")
    print(f"🎵 Файл аудио: {audio_file}")
    
    # Создаем имя выходного файла
    base_name = os.path.splitext(video_file)[0]
    output_file = f"{base_name}_merged.mp4"
    
    print(f"\n🔄 Объединение в файл: {output_file}")
    
    # Объединяем файлы, не передавая путь к ffmpeg
    success, message = merge_files(video_file, audio_file, output_file)
    
    if success:
        print(f"✅ {message}")
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"📁 Результат: {output_file} ({size_mb:.1f} MB)")
    else:
        print(f"❌ Ошибка: {message}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()