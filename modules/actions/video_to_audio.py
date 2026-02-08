import os
import json
from pydub import AudioSegment

class VideoToAudioAction:
    def __init__(self, filepath):
        self.filepath = filepath
        self.dir, self.name = os.path.split(filepath)
        self.base, self.ext = os.path.splitext(self.name)

    def video_to_audio(self):
        settings_path = os.path.join(os.path.dirname(__file__), "..", "..", "audio_settings.json")
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)

        format_type = settings.get("format", "mp3")
        bitrate = settings.get("bitrate", "192k")
        frequency = settings.get("frequency", 44100)

        video_path = self.filepath
        audio_path = os.path.join(self.dir, f"{self.base}.{format_type}")

        video = AudioSegment.from_file(video_path)
        audio = video.set_frame_rate(frequency)
        audio.export(audio_path, format=format_type, bitrate=bitrate)
        print(f"✅ Аудио извлечено: {audio_path}")