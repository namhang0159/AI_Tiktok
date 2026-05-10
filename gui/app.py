from controller.ai_controller import TikTokAIController
from gui.modals import LoadingModal, VoiceModal, VoiceError
from services.db_service import init_db, copy_to_clipboard

import customtkinter as ctk
import cv2
from PIL import Image
import sqlite3
import time
import pyautogui

# ======================
# GUI
# ======================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TikTok AI Controller")
        self.geometry("1100x600")

        init_db()
        self.controller = TikTokAIController()
        self.cap = cv2.VideoCapture(0)
        self.loading_modal = None
        self.current_voice_modal = None

        self.grid_columnconfigure(1, weight=1)

        sidebar = ctk.CTkFrame(self, width=250)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(sidebar, text="HỆ THỐNG AI", font=("Arial", 20, "bold")).pack(pady=20)

        self.txt_logs = ctk.CTkTextbox(sidebar, width=200, height=300)
        self.txt_logs.pack(pady=10)

        ctk.CTkButton(sidebar, text="Xem lịch sử", command=self.show_history).pack(pady=10)
        
        # Greeting label
        self.greeting = ctk.CTkLabel(sidebar, text="", font=("Arial", 14, "bold"), text_color="cyan")
        self.greeting.pack(pady=10)

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.grid(row=0, column=1, sticky="nsew")

        self.status = ctk.CTkLabel(self, text="Hành động: None", font=("Arial", 16))
        self.status.grid(row=1, column=1)

        self.update_frame()

    def show_history(self):
        conn = sqlite3.connect('tiktok_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT action_name, timestamp FROM logs ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()

        self.txt_logs.delete("1.0", "end")
        for r in rows:
            self.txt_logs.insert("end", f"{r[1]}: {r[0]}\n")

        conn.close()

    def show_loading_modal(self):
        if self.loading_modal:
            try:
                self.loading_modal.destroy()
            except:
                pass
        self.loading_modal = LoadingModal(self)

    def hide_loading_modal(self):
        if self.loading_modal:
            try:
                self.loading_modal.destroy()
            except:
                pass
            self.loading_modal = None

    def show_voice_modal(self, text):
        modal = VoiceModal(self, self.send_comment)
        modal.set_text(text)
        self.current_voice_modal = modal
        return modal

    def show_voice_error(self):
        error = VoiceError(self)

    def send_comment(self, text):
        """Gửi comment bằng clipboard"""
        try:
            # Copy text to clipboard
            if copy_to_clipboard(text):
                print(f"📋 Copy vào clipboard: {text}")
                time.sleep(0.3)
                
                # Click vào text box
                self.controller.click_icon("icon/comment-tab.png")
                time.sleep(0.5)
                
                # Paste từ clipboard (Ctrl+V)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.3)
                
                # Gửi (Enter)
                pyautogui.press("enter")
                time.sleep(0.3)
                # Di chuyển ra ngoài trường comment để tránh focus nháy
                pyautogui.press("tab")
                time.sleep(0.2)
                pyautogui.press("tab")
                time.sleep(0.2)
                print("✓ Gửi comment thành công")
            else:
                print("❌ Không thể copy vào clipboard")
        except Exception as e:
            print(f"❌ Lỗi gửi comment: {e}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame, action, gender_greeting = self.controller.process_frame(frame, self)

            # Ưu tiên hiển thị action, nếu không có thì hiển thị gender greeting
            # Hiển thị action
            if action != "None":
                self.status.configure(text=f"Hành động: {action}")
            else:
                self.status.configure(text="Hành động: None")

            # Hiển thị greeting riêng
            if gender_greeting != "None":
                self.greeting.configure(text=gender_greeting)
            else:
                self.greeting.configure(text="")

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 500))

            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img

        self.after(20, self.update_frame)
