import ffmpeg
import os
import sys
import multiprocessing
import psutil
import time
from pathlib import Path
import concurrent.futures
from typing import Dict, List
import subprocess

class CarVideoConverter:
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.gpu_available = self._check_gpu_support()
        self.video_presets = {
            "economy": {
                "name": "Эконом (меньше места)",
                "video_codec": "libx264",
                "video_bitrate": "1500k",
                "max_bitrate": "2000k",
                "resolution": "1280x640",
                "fps": 24,
                "preset": "ultrafast",
                "threads": self._get_optimal_threads()
            },
            "balanced": {
                "name": "Баланс (оптимально)",
                "video_codec": "libx264",
                "video_bitrate": "3000k",
                "max_bitrate": "4000k",
                "resolution": "1920x960",
                "fps": 30,
                "preset": "veryfast",
                "threads": self._get_optimal_threads()
            },
            "quality": {
                "name": "Качество (лучшее)",
                "video_codec": "libx264",
                "video_bitrate": "5000k",
                "max_bitrate": "6000k",
                "resolution": "1920x960",
                "fps": 30,
                "preset": "faster",
                "threads": self._get_optimal_threads()
            },
            "ultra": {
                "name": "Ультра (максимум)",
                "video_codec": "libx265",
                "video_bitrate": "6000k",
                "max_bitrate": "7000k",
                "resolution": "1920x960",
                "fps": 30,
                "preset": "fast",
                "threads": self._get_optimal_threads()
            }
        }
        self.audio_settings = {
            "codec": "aac",
            "bitrate": "320k",
            "sample_rate": 48000,
            "channels": 2
        }
        self.performance_settings = {
            "max_workers": min(self.cpu_count, 4),
            "buffer_size": "16M",
            "slice_count": self.cpu_count
        }

    def _check_gpu_support(self) -> bool:
        """Проверка поддержки GPU ускорения"""
        try:
            # Указываем полный путь к ffmpeg
            ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
            result = subprocess.run([ffmpeg_exe, '-encoders'], 
                                  capture_output=True, text=True, timeout=30)
            if 'h264_nvenc' in result.stdout or 'hevc_nvenc' in result.stdout:
                return True
        except Exception as e:
            print(f"GPU проверка: {e}")
            pass
        return False

    def _get_optimal_threads(self) -> int:
        """Оптимальное количество потоков для кодирования"""
        return max(1, int(self.cpu_count * 0.75))

    def _get_gpu_preset(self, preset_name: str) -> dict:
        """Возвращает GPU-ускоренный пресет если доступно"""
        if not self.gpu_available:
            return self.video_presets[preset_name]
        gpu_presets = {
            "economy": {
                "video_codec": "h264_nvenc",
                "preset": "p4",
                "profile:v": "baseline"
            },
            "balanced": {
                "video_codec": "h264_nvenc", 
                "preset": "p3",
                "profile:v": "main"
            },
            "quality": {
                "video_codec": "h264_nvenc",
                "preset": "p2",
                "profile:v": "high"
            },
            "ultra": {
                "video_codec": "hevc_nvenc",
                "preset": "p3",
                "profile:v": "main"
            }
        }
        base_preset = self.video_presets[preset_name].copy()
        if preset_name in gpu_presets:
            base_preset.update(gpu_presets[preset_name])
        return base_preset

    def convert_single_file(self, input_file: str, output_file: str, 
                          preset_name: str = "balanced") -> dict:
        try:
            if not os.path.exists(input_file):
                return {"success": False, "error": f"Файл не найден: {input_file}"}
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            input_path_obj = Path(input_file)
            output_path_obj = Path(output_file)
            if input_path_obj.resolve() == output_path_obj.resolve():
                temp_output = output_path_obj.parent / f"temp_{output_path_obj.name}"
                final_output = output_file
                output_file = str(temp_output)
            else:
                temp_output = None
                final_output = None

            preset = self._get_gpu_preset(preset_name) if self.gpu_available \
                    else self.video_presets[preset_name]
            audio = self.audio_settings

            print(f"Конвертация: {input_path_obj.name}")
            print(f"Пресет: {preset['name']}")
            print(f"GPU ускорение: {'Да' if self.gpu_available else 'Нет'}")

            video_args = {
                'vcodec': preset['video_codec'],
                'b:v': preset['video_bitrate'],
                'maxrate': preset['max_bitrate'],
                'bufsize': str(int(preset['max_bitrate'].replace('k','')) * 2) + 'k',
                'vf': f"scale={preset['resolution']}",
                'r': preset['fps'],
                'preset': preset['preset'],
                'threads': preset['threads'],
                'flags': '+low_delay',
                'movflags': '+faststart',
            }

            if 'profile:v' in preset:
                video_args['profile:v'] = preset['profile:v']

            audio_args = {
                'acodec': audio['codec'],
                'b:a': audio['bitrate'],
                'ar': audio['sample_rate'],
                'ac': audio['channels'],
                'q:a': 0,
                'profile:a': 'aac_low'
            }

            # Указываем полный путь к ffmpeg
            ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
            
            (
                ffmpeg
                .input(input_file)
                .output(output_file, **video_args, **audio_args)
                .overwrite_output()
                .global_args('-y')
                .global_args('-hide_banner')
                .global_args('-loglevel', 'error')
                .run(cmd=ffmpeg_exe)  # Указываем путь к ffmpeg
            )

            if temp_output and final_output:
                temp_output.replace(final_output)

            return {"success": True, "error": None}
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg ошибка: {e.stderr.decode() if e.stderr else str(e)}"
            print(f"❌ Ошибка конвертации {input_file}: {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Общая ошибка: {str(e)}"
            print(f"❌ Ошибка конвертации {input_file}: {error_msg}")
            return {"success": False, "error": error_msg}

    def batch_convert(self, input_files: List[str], output_dir: str = ".", 
                     preset_name: str = "balanced") -> Dict[str, dict]:
        """Пакетная конвертация с сохранением в указанной папке"""
        results = {}
        for i, input_file in enumerate(input_files):
            input_path = Path(input_file)
            if output_dir == "." or output_dir == str(input_path.parent):
                output_file = input_path.parent / f"{input_path.stem}_converted.mp4"
            else:
                output_file = Path(output_dir) / f"{input_path.stem}_converted.mp4"

            counter = 1
            while output_file.exists():
                if output_dir == "." or output_dir == str(input_path.parent):
                    output_file = input_path.parent / f"{input_path.stem}_converted_{counter}.mp4"
                else:
                    output_file = Path(output_dir) / f"{input_path.stem}_converted_{counter}.mp4"
                counter += 1

            print(f"[{i+1}/{len(input_files)}] Обработка: {input_path.name}")
            result = self.convert_single_file(str(input_path), str(output_file), preset_name)
            results[input_file] = result
            if result["success"]:
                print(f"✅ Успешно → {output_file.name}")
            else:
                print(f"❌ Ошибка: {result['error']}")
        return results

    def auto_preset_selection(self, file_size_mb: float) -> str:
        """Автоматический выбор пресета на основе размера файла"""
        if file_size_mb > 8000:
            return "economy"
        elif file_size_mb > 4000:
            return "balanced"
        elif file_size_mb > 2000:
            return "quality"
        else:
            return "ultra"

    def get_system_info(self) -> str:
        """Получение информации о системе"""
        info = f"""
💻 Системная информация:
   CPU: {self.cpu_count} ядер
   RAM: {self.memory_gb:.1f} ГБ
   GPU ускорение: {'Да' if self.gpu_available else 'Нет'}
        """
        return info

def find_video_files(directory: str = r'D:\Converters') -> List[str]:
    """Поиск видео файлов в директории D:\Converters"""
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
    video_files = []
    path = Path(directory)
    for file in path.iterdir():
        if file.is_file() and file.suffix.lower() in video_extensions:
            video_files.append(str(file))
    return video_files

def main():
    # Фиксированный путь к папке Converters
    folder_path = r'D:\Converters'
    
    # Проверяем существование папки
    if not os.path.exists(folder_path):
        print(f"❌ Папка {folder_path} не существует!")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    # Проверяем, доступен ли ffmpeg по указанному пути
    ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
    if not os.path.exists(ffmpeg_exe):
        print(f"❌ FFmpeg не найден по пути: {ffmpeg_exe}")
        print("Убедитесь, что ffmpeg установлен правильно")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    
    try:
        subprocess.run([ffmpeg_exe, '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg не работает корректно!")
        print(f"Путь к ffmpeg: {ffmpeg_exe}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    converter = CarVideoConverter()
    print("🚀 Авто Видео Конвертер (2:1 соотношение сторон)")
    print(converter.get_system_info())
    print(f"🔍 Поиск видео файлов в папке: {folder_path}")
    
    input_files = find_video_files(folder_path)
    
    if not input_files:
        print("❌ В папке D:\\Converters не найдено видео файлов для конвертации.")
        print("Поддерживаемые форматы: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm")
        input("Нажмите Enter для выхода...")
        return

    print(f"📥 Найдено файлов: {len(input_files)}")
    for file in input_files:
        print(f"   - {Path(file).name}")

    print("\n⚙️  Выберите пресет качества:")
    print("   1. Economy (меньше места, 1280x640)")
    print("   2. Balanced (баланс, 1920x960) [по умолчанию]")
    print("   3. Quality (лучшее качество, 1920x960)")
    print("   4. Ultra (максимум, H.265, 1920x960)")
    print("   5. Auto (автоматический выбор по размеру файла)")

    choice = input("\nВведите номер (1-5) или нажмите Enter для Balanced: ").strip()
    
    preset_map = {
        "1": "economy",
        "2": "balanced", 
        "3": "quality",
        "4": "ultra",
        "5": "auto"
    }
    
    if choice in preset_map:
        preset_choice = preset_map[choice]
    else:
        preset_choice = "balanced"

    auto_preset = (preset_choice == "auto")
    if not auto_preset and preset_choice != "balanced":
        preset_name = preset_choice
    else:
        preset_name = "balanced"

    print(f"\n🎯 Выбран режим: {'Автоматический' if auto_preset else converter.video_presets[preset_name]['name']}")
    
    start_time = time.time()
    
    if auto_preset:
        print("🔄 Автоматический выбор пресетов...")
        results = {}
        for input_file in input_files:
            try:
                size_mb = os.path.getsize(input_file) / (1024 * 1024)
                preset = converter.auto_preset_selection(size_mb)
                input_path = Path(input_file)
                output_file = input_path.parent / f"{input_path.stem}_converted.mp4"
                counter = 1
                while output_file.exists():
                    output_file = input_path.parent / f"{input_path.stem}_converted_{counter}.mp4"
                    counter += 1

                print(f"\nОбработка: {input_path.name} ({size_mb:.1f} МБ)")
                print(f"Выбран пресет: {converter.video_presets[preset]['name']}")
                result = converter.convert_single_file(str(input_path), str(output_file), preset)
                results[input_file] = result
                if result["success"]:
                    print(f"✅ Успешно → {output_file.name}")
                else:
                    print(f"❌ Ошибка: {result['error']}")
            except Exception as e:
                results[input_file] = {"success": False, "error": str(e)}
    else:
        print(f"🚀 Начало конвертации с пресетом: {converter.video_presets[preset_name]['name']}")
        results = converter.batch_convert(input_files, folder_path, preset_name)

    end_time = time.time()
    duration = end_time - start_time

    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   Успешно: {successful}/{len(results)}")
    print(f"   Время: {duration:.1f} секунд")
    if duration > 0 and successful > 0:
        print(f"   Скорость: {successful/duration:.2f} файлов/сек")

    if successful < len(results):
        print(f"\n⚠️  Ошибок: {len(results) - successful}")
        failed_files = [f for f, r in results.items() if not r["success"]]
        for failed_file in failed_files[:5]:
            print(f"   - {Path(failed_file).name}")
        if len(failed_files) > 5:
            print(f"   ... и ещё {len(failed_files) - 5} файлов")

    print(f"\n📁 Сконвертированные файлы сохранены в папке: {folder_path}")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)