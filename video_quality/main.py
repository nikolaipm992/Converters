import os
import ffmpeg
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import sys
from threading import Lock
import time

INPUT_FOLDER = "."
OUTPUT_SUFFIX = "converted_"
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm'}
FFMPEG_PATH = r"D:\codecff\ffmpeg.exe"

QUALITY_PRESETS = {
    "1": {"name": "Эконом (480p)", "crf": 28, "resolution": "854:480"},
    "2": {"name": "Стандарт (720p)", "crf": 23, "resolution": "1280:720"},
    "3": {"name": "HD (1080p)", "crf": 18, "resolution": "1920:1080"},
    "4": {"name": "Высокое (1080p+)", "crf": 16, "resolution": "1920:1080"}
}

print_lock = Lock()
global_progress = 0
total_progress_parts = 0
progress_lock = Lock()

def check_gpu_support():
    """Проверяет доступные GPU кодеки и возвращает лучший"""
    try:
        # Проверяем в порядке приоритета
        gpu_codecs = [
            ('h264_nvenc', 'NVIDIA RTX 3060'),  # NVIDIA GPU
            ('h264_qsv', 'Intel Quick Sync'),   # Intel GPU
            ('h264_vaapi', 'Intel VAAPI')       # Альтернатива Intel
        ]
        
        for codec, name in gpu_codecs:
            try:
                # Пробуем создать тестовый файл
                (
                    ffmpeg
                    .input('test', t=1)
                    .output('test.mp4', vcodec=codec, pix_fmt='yuv420p')
                    .run(cmd=FFMPEG_PATH, overwrite_output=True, capture_stdout=True, capture_stderr=True)
                )
                if os.path.exists('test.mp4'):
                    os.remove('test.mp4')
                return codec, name
            except:
                continue
        return None, None
    except:
        return None, None

def get_quality_choice():
    print("\n🎬 Выберите качество видео на выходе:")
    print("-" * 40)
    for key, preset in QUALITY_PRESETS.items():
        print(f"{key}. {preset['name']}")
    print("-" * 40)
    
    while True:
        choice = input("Введите номер качества (1-4): ").strip()
        if choice in QUALITY_PRESETS:
            return QUALITY_PRESETS[choice]
        print("❌ Неверный выбор. Попробуйте еще раз.")

def get_processing_options():
    # Проверяем GPU
    gpu_codec, gpu_name = check_gpu_support()
    use_gpu = False
    
    if gpu_codec:
        print(f"\n⚡ Найден GPU: {gpu_name} ({gpu_codec})")
        gpu_choice = input("Использовать GPU для ускорения? (y/n, по умолчанию y): ").strip().lower()
        use_gpu = gpu_choice in ['y', 'yes', 'д', 'да', '']
        if use_gpu:
            print(f"🎮 Будет использоваться: {gpu_name}")
    else:
        print("\n💻 GPU ускорение недоступно")
    
    # Количество потоков
    cpu_count = multiprocessing.cpu_count()
    
    # Оптимальные настройки для ноутбука
    if use_gpu:
        # При GPU используем меньше CPU потоков
        recommended_threads = min(4, cpu_count // 2)
        print(f"\n💡 Рекомендация для ноутбука с GPU: {recommended_threads} потоков")
    else:
        # Без GPU используем больше потоков, но не все
        recommended_threads = min(8, max(cpu_count // 2, 2))
        print(f"\n💡 Рекомендация для ноутбука: {recommended_threads} потоков")
    
    print(f"🖥️  Доступно ядер CPU: {cpu_count}")
    
    while True:
        try:
            threads_input = input(f"Количество потоков (1-{cpu_count}, по умолчанию {recommended_threads}): ").strip()
            if not threads_input:
                max_workers = recommended_threads
                break
            max_workers = int(threads_input)
            if 1 <= max_workers <= cpu_count:
                break
            else:
                print(f"Введите число от 1 до {cpu_count}")
        except ValueError:
            print("Введите корректное число")
    
    return use_gpu, max_workers, gpu_codec

def get_video_duration(input_path):
    try:
        probe = ffmpeg.probe(input_path, cmd=FFMPEG_PATH.replace('ffmpeg.exe', 'ffprobe.exe'))
        duration = float(probe['format']['duration'])
        return duration
    except:
        return None

def update_global_progress(parts_completed):
    global global_progress
    with progress_lock:
        global_progress += parts_completed
        if total_progress_parts > 0:
            percent = (global_progress / total_progress_parts) * 100
            with print_lock:
                print(f"\r📊 Общий прогресс: {percent:.1f}% ({global_progress}/{total_progress_parts})", end='', flush=True)

def convert_video_detailed_progress(input_path, output_path, quality_preset, use_gpu=False, gpu_codec=None, total_files=1, current_file=1):
    try:
        filename = Path(input_path).name
        
        quality_suffix = {
            "854:480": "_480p",
            "1280:720": "_720p", 
            "1920:1080": "_1080p"
        }.get(quality_preset["resolution"], "_HD")
        
        duration = get_video_duration(input_path)
        if not duration:
            duration = 3600
        
        stream = ffmpeg.input(input_path)
        
        # Масштабирование с оптимизацией для ноутбука
        if quality_preset["resolution"] == "1920:1080":
            scale_filter = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,unsharp=5:5:1.0'
        elif quality_preset["resolution"] == "1280:720":
            scale_filter = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,unsharp=5:5:0.8'
        else:
            scale_filter = f'scale={quality_preset["resolution"]}:force_original_aspect_ratio=decrease,pad={quality_preset["resolution"]}:(ow-iw)/2:(oh-ih)/2,unsharp=5:5:0.5'
        
        # Параметры вывода с оптимизацией для ноутбука
        output_params = {
            'acodec': 'aac',
            'audio_bitrate': '320k',
            'pix_fmt': 'yuv420p'
        }
        
        # Выбор кодека с оптимизацией для ноутбука
        if use_gpu and gpu_codec:
            output_params['vcodec'] = gpu_codec
            
            # Оптимизированные параметры для разных GPU
            if gpu_codec == 'h264_nvenc':
                # Параметры для RTX 3060
                output_params.update({
                    'preset': 'p4',           # Баланс скорость/качество
                    'cq': quality_preset["crf"],
                    'b_ref_mode': '2',        # Улучшенные B-кадры
                    'rc': 'vbr',              # Variable bitrate
                    'cq_profile': 'high_quality', # Профиль качества
                    'gpu': 'any'              # Использовать любую доступную GPU
                })
            elif gpu_codec == 'h264_qsv':
                # Параметры для Intel GPU
                output_params.update({
                    'preset': 'veryfast',
                    'global_quality': quality_preset["crf"],
                    'async_depth': '4',       # Асинхронная обработка
                })
            elif gpu_codec == 'h264_vaapi':
                output_params.update({
                    'compression_level': '7',
                    'quality': 'good',
                })
            print(f"⚡ Используется GPU ускорение ({gpu_codec})")
        else:
            # Оптимизированные параметры для CPU на ноутбуке
            output_params.update({
                'vcodec': 'libx264',
                'preset': 'fast',             # Быстрое кодирование
                'crf': quality_preset["crf"],
                'threads': '0',               # Автоопределение потоков
                'profile:v': 'high',          # Высокий профиль
                'level': '4.2'                # Совместимость
            })
        
        output_params['vf'] = scale_filter
        
        print(f"\n🔄 [{current_file}/{total_files}] Конвертирую: {filename}")
        print(f"🎯 Качество: {quality_preset['name']}")
        
        start_time = time.time()
        
        process = (
            stream
            .output(output_path, **output_params)
            .run_async(cmd=FFMPEG_PATH, pipe_stderr=True, overwrite_output=True)
        )
        
        parts_completed = 0
        last_update = 0
        
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line_str = line.decode('utf-8', errors='ignore')
                if 'frame=' in line_str or 'fps=' in line_str:
                    current_part = min(int((parts_completed / 100) * 1000), 1000)
                    if current_part > last_update:
                        parts_to_update = current_part - last_update
                        if parts_to_update > 0:
                            update_global_progress(parts_to_update)
                            last_update = current_part
                    parts_completed += 1
        
        process.wait()
        
        remaining_parts = 1000 - last_update
        if remaining_parts > 0:
            update_global_progress(remaining_parts)
        
        if process.returncode == 0:
            elapsed_time = time.time() - start_time
            print(f"\n✅ [{current_file}/{total_files}] Готово: {Path(output_path).name} ({elapsed_time:.1f}с)")
            return True, input_path
        else:
            print(f"\n❌ [{current_file}/{total_files}] Ошибка: {filename}")
            return False, input_path
        
    except Exception as e:
        print(f"\n❌ [{current_file}/{total_files}] Ошибка при конвертации {filename}: {e}")
        return False, input_path

def find_video_files(root_dir):
    root_path = Path(root_dir).absolute()
    video_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in VIDEO_EXTENSIONS:
                video_files.append((str(file_path), dirpath, filename))
    
    return video_files

def process_videos_parallel(video_files, quality_preset, use_gpu, gpu_codec, max_workers):
    global global_progress, total_progress_parts
    root_path = Path(INPUT_FOLDER).absolute()
    output_root = root_path.parent / (OUTPUT_SUFFIX + root_path.name)
    
    quality_suffix = {
        "854:480": "_480p",
        "1280:720": "_720p", 
        "1920:1080": "_1080p"
    }.get(quality_preset["resolution"], "_HD")
    
    processed_count = 0
    error_count = 0
    total_files = len(video_files)
    total_progress_parts = total_files * 1000
    
    print(f"\n🚀 Начинаю обработку {total_files} файлов...")
    print(f"⚡ Потоков: {max_workers}")
    if use_gpu and gpu_codec:
        gpu_name = {'h264_nvenc': 'NVIDIA RTX 3060', 'h264_qsv': 'Intel Quick Sync', 'h264_vaapi': 'Intel VAAPI'}.get(gpu_codec, gpu_codec)
        print(f"🎮 Используется GPU ускорение ({gpu_name})")
    print("-" * 60)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_info = {}
        file_counter = 1
        
        for input_path, dirpath, filename in video_files:
            rel_dir = Path(dirpath).relative_to(root_path)
            output_dir = output_root / rel_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / (Path(filename).stem + quality_suffix + ".mp4")
            
            future = executor.submit(
                convert_video_detailed_progress, 
                input_path, 
                str(output_file), 
                quality_preset, 
                use_gpu, 
                gpu_codec,
                total_files, 
                file_counter
            )
            future_to_info[future] = (filename, file_counter)
            file_counter += 1
        
        completed_count = 0
        for future in as_completed(future_to_info):
            filename, file_num = future_to_info[future]
            success, input_path = future.result()
            
            completed_count += 1
            if success:
                processed_count += 1
            else:
                error_count += 1
    
    return processed_count, error_count

def main():
    global global_progress, total_progress_parts
    print("🎥 Конвертер видео с выбором качества")
    print("🔊 Аудио всегда на максимуме (320 кбит/с)")
    print("💻 Оптимизирован для ноутбука с двойным GPU")
    print("=" * 45)
    
    try:
        quality_preset = get_quality_choice()
        use_gpu, max_workers, gpu_codec = get_processing_options()
        
        print(f"\n🔍 Ищу видео файлы в: {INPUT_FOLDER}")
        video_files = find_video_files(INPUT_FOLDER)
        
        if not video_files:
            print("❌ Видео файлы не найдены")
            return
        
        print(f"📁 Найдено файлов: {len(video_files)}")
        
        print(f"\n⚠️  Будут конвертированы {len(video_files)} видео")
        print("🔊 Аудио будет на максимальном качестве (320 кбит/с)")
        confirm = input("Продолжить? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', 'д', 'да', '']:
            global_progress = 0
            total_progress_parts = len(video_files) * 1000
            processed, errors = process_videos_parallel(video_files, quality_preset, use_gpu, gpu_codec, max_workers)
            print("\n" + "-" * 60)
            print(f"📊 Результаты:")
            print(f"✅ Успешно обработано: {processed}")
            print(f"❌ Ошибок: {errors}")
            if processed + errors > 0 and total_progress_parts > 0:
                success_rate = (processed / (processed + errors)) * 100
                print(f"📈 Процент успеха: {success_rate:.1f}%")
            print("🎉 Обработка завершена!")
        else:
            print("❌ Операция отменена")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Операция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()