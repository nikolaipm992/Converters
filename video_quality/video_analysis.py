import subprocess
import os
import re
from pathlib import Path

def analyze_video_file(filepath):
    """Анализирует один видеофайл с помощью ffmpeg - полная информация"""
    try:
        # Выполняем команду ffmpeg -i для получения информации
        result = subprocess.run([
            'ffmpeg', '-i', str(filepath)
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        # ffmpeg выводит информацию в stderr
        output = result.stderr
        
        # Извлекаем основную информацию
        info = {}
        
        # Длительность
        duration_match = re.search(r'Duration: ([\d:.]+)', output)
        if duration_match:
            info['duration'] = duration_match.group(1)
        
        # Видео поток
        video_match = re.search(r'Stream.*Video:.*', output)
        if video_match:
            video_info = video_match.group(0)
            # Извлекаем разрешение
            res_match = re.search(r'(\d{3,4}x\d{3,4})', video_info)
            info['resolution'] = res_match.group(1) if res_match else 'Unknown'
            # Извлекаем кодек
            codec_match = re.search(r'Video: ([^, ]+)', video_info)
            info['video_codec'] = codec_match.group(1) if codec_match else 'Unknown'
            # Извлекаем битрейт
            bitrate_match = re.search(r'(\d+)\s*kb/s', video_info)
            info['video_bitrate'] = bitrate_match.group(1) + ' kb/s' if bitrate_match else 'Unknown'
            # Извлекаем FPS
            fps_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', video_info)
            info['fps'] = fps_match.group(1) if fps_match else 'Unknown'
        
        # Аудио поток
        audio_match = re.search(r'Stream.*Audio:.*', output)
        if audio_match:
            audio_info = audio_match.group(0)
            # Извлекаем аудио кодек
            a_codec_match = re.search(r'Audio: ([^, ]+)', audio_info)
            info['audio_codec'] = a_codec_match.group(1) if a_codec_match else 'Unknown'
            # Извлекаем аудио битрейт
            a_bitrate_match = re.search(r'(\d+)\s*kb/s', audio_info)
            info['audio_bitrate'] = a_bitrate_match.group(1) + ' kb/s' if a_bitrate_match else 'Unknown'
            # Извлекаем частоту дискретизации
            a_freq_match = re.search(r'(\d+)\s*Hz', audio_info)
            info['audio_frequency'] = a_freq_match.group(1) + ' Hz' if a_freq_match else 'Unknown'
            # Извлекаем количество каналов
            if 'stereo' in audio_info:
                info['audio_channels'] = 'stereo'
            elif 'mono' in audio_info:
                info['audio_channels'] = 'mono'
            else:
                info['audio_channels'] = 'Unknown'
        
        return info
    
    except Exception as e:
        return {'error': str(e)}

def analyze_all_videos_in_folder(folder_path, extensions=None):
    """Анализирует все видеофайлы в папке"""
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    
    folder = Path(folder_path)
    video_files = [f for f in folder.iterdir() 
                   if f.is_file() and f.suffix.lower() in extensions]
    
    results = {}
    
    for video_file in video_files:
        print(f"Анализ файла: {video_file.name}")
        info = analyze_video_file(video_file)
        results[video_file.name] = info
    
    return results

def print_results(results):
    """Выводит результаты в удобочитаемом формате"""
    print("\n" + "="*80)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА ВИДЕОФАЙЛОВ")
    print("="*80)
    
    for filename, info in results.items():
        print(f"\n📁 Файл: {filename}")
        print("-" * 60)
        
        if 'error' in info:
            print(f"❌ Ошибка: {info['error']}")
            continue
        
        # Основная информация
        print(f"⏱️  Длительность: {info.get('duration', 'N/A')}")
        print(f"📺 Разрешение: {info.get('resolution', 'N/A')}")
        print(f"🎬 Видео кодек: {info.get('video_codec', 'N/A')}")
        print(f"📊 Видео битрейт: {info.get('video_bitrate', 'N/A')}")
        print(f"⚡ FPS: {info.get('fps', 'N/A')}")
        print(f"🎵 Аудио кодек: {info.get('audio_codec', 'N/A')}")
        print(f"🔊 Аудио битрейт: {info.get('audio_bitrate', 'N/A')}")
        print(f"🎼 Частота дискретизации: {info.get('audio_frequency', 'N/A')}")
        print(f"🎧 Каналы: {info.get('audio_channels', 'N/A')}")

def save_results_to_file(results, output_file):
    """Сохраняет результаты в текстовый файл"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("АНАЛИЗ ВИДЕОФАЙЛОВ\n")
        f.write("="*50 + "\n\n")
        
        for filename, info in results.items():
            f.write(f"Файл: {filename}\n")
            f.write("-" * 30 + "\n")
            
            if 'error' in info:
                f.write(f"Ошибка: {info['error']}\n")
                continue
            
            f.write(f"Длительность: {info.get('duration', 'N/A')}\n")
            f.write(f"Разрешение: {info.get('resolution', 'N/A')}\n")
            f.write(f"Видео кодек: {info.get('video_codec', 'N/A')}\n")
            f.write(f"Видео битрейт: {info.get('video_bitrate', 'N/A')}\n")
            f.write(f"FPS: {info.get('fps', 'N/A')}\n")
            f.write(f"Аудио кодек: {info.get('audio_codec', 'N/A')}\n")
            f.write(f"Аудио битрейт: {info.get('audio_bitrate', 'N/A')}\n")
            f.write(f"Частота дискретизации: {info.get('audio_frequency', 'N/A')}\n")
            f.write(f"Каналы: {info.get('audio_channels', 'N/A')}\n")
            f.write("\n")

# Основной код
if __name__ == "__main__":
    # Укажите путь к папке с видеофайлами
    folder_path = "."  # Текущая папка, можно изменить
    
    print("Начинаем анализ видеофайлов...")
    print(f"Папка: {os.path.abspath(folder_path)}")
    
    # Анализируем все видеофайлы
    results = analyze_all_videos_in_folder(folder_path)
    
    # Выводим результаты
    print_results(results)
    
    # Сохраняем в файл
    save_results_to_file(results, "video_analysis_result.txt")
    print(f"\n📊 Результаты сохранены в файл: video_analysis_result.txt")
    
    # Выводим краткую сводку
    print(f"\n📈 Всего проанализировано файлов: {len(results)}")