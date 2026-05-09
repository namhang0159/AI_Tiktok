from services.db_service import save_log
from services.gender_service import GenderDetector
from services.voice_service import VoiceGreeter
import cv2
import mediapipe as mp
import pyautogui
import pickle
import time
import os
import numpy as np
import threading
import whisper
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

# ======================
# AI CONTROLLER
# ======================
class TikTokAIController:
    def __init__(self):
        if not os.path.exists("model.pkl"):
            raise Exception("Chưa có model.pkl")

        with open("model.pkl", "rb") as f:
            self.model = pickle.load(f)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils
        self.recognizer = sr.Recognizer()

        self.last_action_time = 0
        self.cooldown = 1.5
        self.is_listening = False

        self.prev_pred = None
        self.stable_count = 0
        
        # Gender detection
        try:
            self.gender_detector = GenderDetector()
            print("✅ Gender detector initialized")
        except Exception as e:
            print(f"⚠️ Gender detector error: {e}")
            self.gender_detector = None
        
        # Voice greeter
        self.voice_greeter = VoiceGreeter()
        self.last_greeted_label = None
        self.last_greeted_time = 0
        self.greet_cooldown = 10  # Chỉ chào mỗi 10 giây

    def click_icon(self, path, threshold=0.8):
        screenshot = pyautogui.screenshot()
        screen = np.array(screenshot)
        gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

        template = cv2.imread(path)
        if template is None:
            print(f"❌ Không thể load template: {path}")
            return False

        # Convert to grayscale if necessary
        if len(template.shape) == 3:
            template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        elif len(template.shape) == 4:
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2GRAY)

        h, w = template.shape[:2]  # Get height and width safely

        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val > threshold:
            x, y = max_loc
            pyautogui.click(x + w // 2, y + h // 2)
            return True

        return False

    def process_frame(self, frame, app):
        action_detected = "None"
        gender_greeting = "None"
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                base_x = hand_landmarks.landmark[0].x
                base_y = hand_landmarks.landmark[0].y

                lm_list = []
                for lm in hand_landmarks.landmark:
                    lm_list.append(lm.x - base_x)
                    lm_list.append(lm.y - base_y)

                prediction = self.model.predict([lm_list])[0]

                cv2.putText(frame, f"Pred: {prediction}", (10,50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                # smoothing
                if prediction == self.prev_pred:
                    self.stable_count += 1
                else:
                    self.stable_count = 0
                    self.prev_pred = prediction

                if self.stable_count < 3:
                    return frame, "None", gender_greeting

                if time.time() - self.last_action_time > self.cooldown:
                    action_detected = self.execute_action(prediction, app)
                    if action_detected != "None":
                        self.last_action_time = time.time()
                        save_log(action_detected)
        else:
            # Không có gesture → detect gender
            if self.gender_detector is not None:
                gender_label, gender_name, frame_with_bbox = self.gender_detector.predict_gender(frame)
                
                if gender_label is not None and gender_name is not None:
                    # Draw gender info
                    color = (0, 255, 0) if gender_label == 0 else (255, 0, 0)  # Green for female, blue for male
                    cv2.putText(frame_with_bbox, f"Gender: {gender_name}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                    gender_greeting = "Xin chào cô gái!" if gender_label == 0 else "Xin chào chàng trai!"

                    if gender_label != self.last_greeted_label:
                        self.voice_greeter.greet(gender_label)
                        self.last_greeted_label = gender_label
                        print(f"💬 {gender_greeting}!")

                    frame = frame_with_bbox

        return frame, action_detected, gender_greeting

    def execute_action(self, pred, app):

        if pred == 0:
            pyautogui.scroll(-700)
            return "Cuộn video"

        elif pred == 1:
            if self.click_icon("icon/like.png"):
                return "Thả tim"

        elif pred == 2:
            if self.click_icon("icon/comment.png"):
                return "Mở comment"

        elif pred == 3 and not self.is_listening and getattr(app, "current_voice_modal", None) is None:
            if self.click_icon("icon/comment-tab.png"):
                time.sleep(1)
                threading.Thread(target=self.voice_comment, args=(app,), daemon=True).start()
                return "Voice modal"

        elif pred == 4:
            modal = getattr(app, "current_voice_modal", None)
            if modal is not None:
                modal.send()
                return "Gửi comment"
            return "None"

        return "None"

    def voice_comment(self, app):
        self.is_listening = True
        text = None
        try:
            # Hiển thị loading dialog
            app.after(0, lambda: app.show_loading_modal())
            
            print("🎤 Đang lắng nghe... hãy nói nhận xét (tối đa 15 giây)")
            
            # Record audio từ microphone
            duration = 4  # seconds
            sample_rate = 16000
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            print("🔴 REC...")
            sd.wait()  # Wait for recording to finish
            print("⏹ Recording done")
            
            # Save audio temporarily
            audio_file = "temp_voice.wav"
            sf.write(audio_file, audio_data, sample_rate)
            
            # Load Whisper model (base model for Vietnamese, balanced)
            print("🤖 Loading Whisper model...")
            model = whisper.load_model("base", device="cpu")
            
            # Transcribe
            print("🎯 Recognizing speech...")
            result = model.transcribe(audio_file, language="vi", verbose=False)
            text = result["text"].strip()
            
            # Clean up
            if os.path.exists(audio_file):
                os.remove(audio_file)
            
            if text:
                print(f"✓ Nhận diện: {text}")
                app.after(0, lambda: app.hide_loading_modal())
                app.after(0, lambda: app.show_voice_modal(text))
            else:
                print("❌ Không nhận diện được")
                app.after(0, lambda: app.hide_loading_modal())
                app.after(0, lambda: app.show_voice_error())
                
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            app.after(0, lambda: app.hide_loading_modal())
            app.after(0, lambda: app.show_voice_error())
            
        finally:
            self.is_listening = False
