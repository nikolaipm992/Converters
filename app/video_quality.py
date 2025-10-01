import ffmpeg
import os
import sys
import multiprocessing
import psutil
import time
from pathlib import Path
import subprocess
from typing import Dict, List
import re

class CarVideoConverter:
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.gpu_available = self._check_gpu_support()
        self.torch_available = self._check_torch_support()
        self.realesrgan_path = r"D:\Converters\app\realesrgan"
        self.realesrgan_available = self._check_realesrgan_support()
        
        # Включаем AI если основные компоненты доступны
        ai_enabled = self.torch_available and self.realesrgan_available
        
        self.video_presets = {
            # === Телевизор ===
            "tv_low": {
                "name": "Телевизор (низкое качество)",
                "video_codec": "libx264",
                "video_bitrate": "2500k",
                "max_bitrate": "3000k",
                "resolution": "1280x720",
                "fps": 25,
                "preset": "veryfast",
                "threads": self._get_optimal_threads(),
                "use_ai": ai_enabled,
                "ai_model": "realesr-general-x4v3"
            },
            "tv_medium": {
                "name": "Телевизор (среднее качество)",
                "video_codec": "libx264",
                "video_bitrate": "4500k",
                "max_bitrate": "5500k",
                "resolution": "1920x1080",
                "fps": 30,
                "preset": "faster",
                "threads": self._get_optimal_threads(),
                "use_ai": ai_enabled,
                "ai_model": "realesr-general-x4v3"
            },
            "tv_high": {
                "name": "Телевизор (высокое качество)",
                "video_codec": "libx265",
                "video_bitrate": "6000k",
                "max_bitrate": "7000k",
                "resolution": "1920x1080",
                "fps": 30,
                "preset": "medium",
                "threads": self._get_optimal_threads(),
                "use_ai": ai_enabled,
                "ai_model": "realesr-general-x4v3"
            },

            # === OMODA C5 ===
            "omoda_c5": {
                "name": "OMODA C5 (1920×720, 4.7:1)",
                "video_codec": "libx264",
                "video_bitrate": "3500k",
                "max_bitrate": "4500k",
                "resolution": "1920x720",
                "fps": 30,
                "preset": "faster",
                "threads": self._get_optimal_threads(),
                "use_ai": ai_enabled,
                "ai_model": "realesr-general-x4v3"
            },

            # === Belgee X70 ===
            "belgee_x70": {
                "name": "Belgee X70 (1280×720)",
                "video_codec": "libx264",
                "video_bitrate": "2500k",
                "max_bitrate": "3000k",
                "resolution": "1280x720",
                "fps": 30,
                "preset": "veryfast",
                "threads": self._get_optimal_threads(),
                "use_ai": ai_enabled,
                "ai_model": "realesr-general-x4v3"
            }
        }
        self.audio_settings = {
            "codec": "aac",
            "bitrate": "320k",
            "sample_rate": 48000,
            "channels": 2
        }

    def _check_gpu_support(self) -> bool:
        """Проверка поддержки GPU ускорения"""
        try:
            ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
            result = subprocess.run([ffmpeg_exe, '-encoders'], 
                                  capture_output=True, text=True, timeout=30)
            if 'h264_nvenc' in result.stdout or 'hevc_nvenc' in result.stdout:
                return True
        except Exception as e:
            print(f"GPU проверка: {e}")
            pass
        return False

    def _check_torch_support(self) -> bool:
        """Проверка наличия PyTorch в основном окружении"""
        try:
            import torch
            print(f"✅ PyTorch найден (версия: {torch.__version__})")
            return True
        except ImportError:
            print("❌ PyTorch не найден в основном окружении")
            return False

    def _check_realesrgan_support(self) -> bool:
        """Проверка наличия Real-ESRGAN"""
        script_path = f"{self.realesrgan_path}\\inference_realesrgan_video.py"
        exists = os.path.exists(script_path)
        if exists:
            print("✅ Real-ESRGAN найден")
        else:
            print("❌ Real-ESRGAN не найден")
        return exists

    def _get_optimal_threads(self) -> int:
        """Оптимальное количество потоков для кодирования"""
        return max(1, int(self.cpu_count * 0.75))

    def _get_gpu_preset(self, preset_name: str) -> dict:
        """Возвращает GPU-ускоренный пресет если доступно"""
        if not self.gpu_available:
            return self.video_presets[preset_name]
        gpu_presets = {
            "tv_low": {
                "video_codec": "h264_nvenc",
                "preset": "p4",
                "profile:v": "baseline"
            },
            "tv_medium": {
                "video_codec": "h264_nvenc", 
                "preset": "p3",
                "profile:v": "main"
            },
            "tv_high": {
                "video_codec": "hevc_nvenc",
                "preset": "p3",
                "profile:v": "main"
            },
            "omoda_c5": {
                "video_codec": "h264_nvenc",
                "preset": "p3",
                "profile:v": "main"
            },
            "belgee_x70": {
                "video_codec": "h264_nvenc",
                "preset": "p4",
                "profile:v": "baseline"
            }
        }
        base_preset = self.video_presets[preset_name].copy()
        if preset_name in gpu_presets:
            base_preset.update(gpu_presets[preset_name])
        return base_preset

    def _parse_progress_line(self, line: str) -> tuple:
        """Парсит строку прогресса и возвращает процент и описание"""
        # Ищем паттерны типа "frame 123/456" или "123/456 frames"
        frame_match = re.search(r'(\d+)/(\d+)\s*(?:frames?|frame)', line, re.IGNORECASE)
        if frame_match:
            current = int(frame_match.group(1))
            total = int(frame_match.group(2))
            if total > 0:
                percent = min(100, int((current / total) * 100))
                return percent, f"Обработано {current}/{total} кадров"
        
        # Ищем паттерны типа "25%" или "[25%]"
        percent_match = re.search(r'[\[\(]?\s*(\d+)%\s*[\]\)]?', line)
        if percent_match:
            percent = int(percent_match.group(1))
            return percent, f"{percent}% завершено"
            
        return None, None

    def enhance_with_realesrgan(self, input_file: str, output_file: str, model_name: str = "realesr-general-x4v3") -> bool:
        """Улучшение видео с помощью Real-ESRGAN с отображением прогресса"""
        try:
            # Проверяем базовые требования
            if not (self.torch_available and self.realesrgan_available):
                print("❌ AI улучшение недоступно:")
                if not self.torch_available:
                    print("   - PyTorch не установлен")
                if not self.realesrgan_available:
                    print("   - Real-ESRGAN не найден")
                return False

            print("🚀 Запуск Real-ESRGAN улучшения...")
            
            # Получаем информацию о видео для оценки прогресса
            try:
                probe = ffmpeg.probe(input_file)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream:
                    total_frames = int(video_stream.get('nb_frames', 0))
                    if total_frames > 0:
                        print(f"📊 Общее количество кадров: {total_frames}")
            except:
                total_frames = 0

            # Используем тот же Python, что и для основной программы
            python_exe = sys.executable
            
            # Команда для Real-ESRGAN с указанием полного пути к Python
            cmd = [
                python_exe,
                f"{self.realesrgan_path}\\inference_realesrgan_video.py",
                "-i", input_file,
                "-o", str(Path(output_file).parent),
                "-n", model_name,
                "--suffix", "",  # Без суффикса
                "-s", "4",  # Масштаб 4x
                "--tile", "0",  # Без тайлинга для лучшего качества
                "--fp32" if not self.gpu_available else ""  # FP32 если нет GPU
            ]
            
            # Удаляем пустые аргументы
            cmd = [arg for arg in cmd if arg]
            
            print(f"Команда: {' '.join(cmd)}")
            print(f"Используемый Python: {python_exe}")
            
            # Запуск Real-ESRGAN
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.realesrgan_path,
                bufsize=1,
                universal_newlines=True
            )
            
            # Отслеживание прогресса
            last_percent = 0
            progress_shown = False
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Парсим прогресс
                    percent, description = self._parse_progress_line(output.strip())
                    if percent is not None:
                        if percent != last_percent:
                            last_percent = percent
                            progress_bar = "█" * (percent // 2) + "░" * (50 - percent // 2)
                            print(f"\r  [{progress_bar}] {percent}% {description or ''}", end="", flush=True)
                            progress_shown = True
                    elif "error" in output.lower() or "exception" in output.lower():
                        print(f"\n  ⚠️  {output.strip()}")
                    elif "frame" in output.lower() and ("inference" in output.lower() or "process" in output.lower()):
                        if not progress_shown:
                            print(f"  {output.strip()}")
                    elif "module" in output.lower() and "not found" in output.lower():
                        print(f"\n  ⚠️  {output.strip()}")
                        print("  💡 Попробуйте установить недостающие модули в папку Real-ESRGAN:")
                        print("     cd D:\\codecs\\realesrgan")
                        print("     pip install torch torchvision basicsr")
            
            if progress_shown:
                print()  # Новая строка после прогресса
            
            result = process.poll()
            if result != 0:
                print(f"❌ Real-ESRGAN завершился с кодом ошибки: {result}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка Real-ESRGAN: {e}")
            return False

    def convert_single_file(self, input_file: str, output_file: str, 
                          preset_name: str = "tv_medium") -> dict:
        try:
            if not os.path.exists(input_file):
                return {"success": False, "error": f"Файл не найден: {input_file}"}
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            preset = self._get_gpu_preset(preset_name) if self.gpu_available \
                    else self.video_presets[preset_name]
            audio = self.audio_settings

            print(f"🎬 Конвертация: {Path(input_file).name}")
            print(f"🔧 Пресет: {preset['name']}")
            print(f"🎮 GPU ускорение: {'Да' if self.gpu_available else 'Нет'}")
            
            # Проверяем, будет ли использоваться AI
            ai_will_be_used = preset.get('use_ai', False) and self.torch_available and self.realesrgan_available
            ai_status = "Да" if ai_will_be_used else "Нет"
            if preset.get('use_ai', False) and not (self.torch_available and self.realesrgan_available):
                ai_status += " (недоступно)"
                # Отключаем AI для этой сессии
                preset['use_ai'] = False
            print(f"🤖 AI улучшение: {ai_status}")

            # Если включен AI и доступен, сначала улучшаем видео
            final_input_file = input_file
            if ai_will_be_used:
                print("🔄 AI улучшение с Real-ESRGAN...")
                temp_enhanced = str(Path(input_file).parent / f"temp_enhanced_{Path(input_file).stem}.mp4")
                
                model_name = preset.get('ai_model', 'realesr-general-x4v3')
                if self.enhance_with_realesrgan(input_file, temp_enhanced, model_name):
                    final_input_file = temp_enhanced
                    print("✅ AI улучшение завершено")
                else:
                    print("⚠️  AI улучшение не удалось, используем оригинал")
                    preset['use_ai'] = False  # Отключаем AI для следующих операций

            # Основная конвертация с прогрессом
            print("🔄 Начало конвертации...")
            
            # Получаем общее количество кадров для отслеживания прогресса
            total_frames = 0
            try:
                probe = ffmpeg.probe(final_input_file)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream:
                    total_frames = int(video_stream.get('nb_frames', 0))
            except:
                pass

            video_args = {
                'vcodec': preset['video_codec'],
                'b:v': preset['video_bitrate'],
                'maxrate': preset['max_bitrate'],
                'bufsize': str(int(preset['max_bitrate'].replace('k','')) * 2) + 'k',
                'vf': f"scale={preset['resolution']}",  # Масштабирование до целевого разрешения
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

            ffmpeg_exe = r"D:\codecs\ffmpeg\ffmpeg.exe"
            
            # Запуск с отслеживанием прогресса
            process = (
                ffmpeg
                .input(final_input_file)
                .output(output_file, **video_args, **audio_args)
                .overwrite_output()
                .global_args('-y')
                .global_args('-hide_banner')
                .global_args('-loglevel', 'verbose')  # Для получения прогресса
                .run_async(cmd=ffmpeg_exe, pipe_stderr=True, pipe_stdout=True)
            )
            
            # Отслеживание прогресса ffmpeg
            frame_count = 0
            last_percent = 0
            
            while True:
                try:
                    line = process.stderr.readline().decode('utf-8', errors='ignore')
                except:
                    break
                    
                if line == '' and process.poll() is not None:
                    break
                if line:
                    # Ищем информацию о кадрах
                    if 'frame=' in line and 'fps=' in line:
                        frame_match = re.search(r'frame=\s*(\d+)', line)
                        if frame_match:
                            frame_count = int(frame_match.group(1))
                            if total_frames > 0:
                                percent = min(100, int((frame_count / total_frames) * 100))
                                if percent != last_percent:
                                    last_percent = percent
                                    progress_bar = "█" * (percent // 2) + "░" * (50 - percent // 2)
                                    print(f"\r  [{progress_bar}] {percent}% ({frame_count}/{total_frames} кадров)", end="", flush=True)
            
            if total_frames > 0:
                print()  # Новая строка после прогресса
            
            # Проверяем результат
            return_code = process.poll()
            if return_code != 0:
                raise Exception(f"FFmpeg завершился с кодом {return_code}")

            # Удаляем временный файл если он был создан
            if final_input_file != input_file:
                try:
                    os.remove(final_input_file)
                except:
                    pass

            return {"success": True, "error": None}
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg ошибка"
            try:
                error_msg = f"FFmpeg ошибка: {e.stderr.decode() if e.stderr else str(e)}"
            except:
                pass
            print(f"❌ Ошибка конвертации {input_file}: {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Общая ошибка: {str(e)}"
            print(f"❌ Ошибка конвертации {input_file}: {error_msg}")
            return {"success": False, "error": error_msg}

    def batch_convert(self, input_files: List[str], output_dir: str = ".", 
                     preset_name: str = "tv_medium") -> Dict[str, dict]:
        """Пакетная конвертация с сохранением в указанной папке"""
        results = {}
        total_files = len(input_files)
        
        for i, input_file in enumerate(input_files):
            print(f"\n📋 [{i+1}/{total_files}] Обработка файла: {Path(input_file).name}")
            
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

            start_time = time.time()
            result = self.convert_single_file(str(input_path), str(output_file), preset_name)
            end_time = time.time()
            
            results[input_file] = result
            if result["success"]:
                try:
                    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
                    duration = end_time - start_time
                    print(f"✅ Успешно → {output_file.name} ({file_size:.1f} MB, {duration:.1f} сек)")
                except:
                    print(f"✅ Успешно → {output_file.name}")
            else:
                print(f"❌ Ошибка: {result['error']}")
        return results

    def auto_preset_selection(self, file_size_mb: float) -> str:
        """Автоматический выбор пресета на основе размера файла"""
        if file_size_mb > 8000:
            return "tv_low"
        elif file_size_mb > 4000:
            return "tv_medium"
        elif file_size_mb > 2000:
            return "tv_high"
        else:
            return "tv_high"

    def get_system_info(self) -> str:
        """Получение информации о системе"""
        info = f"""
💻 Системная информация:
   CPU: {self.cpu_count} ядер
   RAM: {self.memory_gb:.1f} ГБ
   GPU ускорение: {'Да' if self.gpu_available else 'Нет'}
   PyTorch: {'Да' if self.torch_available else 'Нет'}
   Real-ESRGAN: {'Да' if self.realesrgan_available else 'Нет'}
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
    print("🚀 Авто Видео Конвертер для автомобилей и телевизоров")
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
    print("   1. Телевизор (низкое качество, 1280x720)")
    print("   2. Телевизор (среднее качество, 1920x1080) [по умолчанию]")
    print("   3. Телевизор (высокое качество, 1920x1080 H.265)")
    print("   4. OMODA C5 (1920x720, 4.7:1)")
    print("   5. Belgee X70 (1280x720)")
    print("   6. Auto (автоматический выбор по размеру файла)")

    choice = input("\nВведите номер (1-6) или нажмите Enter для Телевизор (среднее): ").strip()
    
    preset_map = {
        "1": "tv_low",
        "2": "tv_medium", 
        "3": "tv_high",
        "4": "omoda_c5",
        "5": "belgee_x70",
        "6": "auto"
    }
    
    if choice in preset_map:
        preset_choice = preset_map[choice]
    else:
        preset_choice = "tv_medium"

    auto_preset = (preset_choice == "auto")
    if not auto_preset and preset_choice != "tv_medium":
        preset_name = preset_choice
    else:
        preset_name = "tv_medium"

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
    print(f"\n📊 РЕЗУЛЬТАТЫ КОНВЕРТАЦИИ:")
    print(f"   ✅ Успешно: {successful}/{len(results)}")
    print(f"   ⏱️  Общее время: {duration:.1f} секунд")
    if duration > 0 and successful > 0:
        print(f"   🚀 Скорость: {successful/duration:.2f} файлов/сек")

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
        print("\n\n⚠️  Прервано пользователем")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        print(f"Трассировка: {traceback.format_exc()}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)