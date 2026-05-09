from gtts import gTTS
import pygame
import threading
import os
import time

class VoiceGreeter:
    def __init__(self):
        pygame.mixer.init()
        self.file_path = "temp_voice.mp3"

    def greet(self, gender_label):
        text = "Xin chào cô gái!" if gender_label == 0 else "Xin chào chàng trai!"
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text):
        try:
            # Nếu đang phát thì dừng
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                time.sleep(0.2)

            # Xóa file cũ
            if os.path.exists(self.file_path):
                try:
                    os.remove(self.file_path)
                except:
                    return

            # Tạo file mới
            tts = gTTS(text=text, lang="vi")
            tts.save(self.file_path)

            # Phát
            pygame.mixer.music.load(self.file_path)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()

        except Exception as e:
            print(f"❌ Lỗi TTS: {e}")