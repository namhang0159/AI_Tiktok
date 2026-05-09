import customtkinter as ctk
import threading
import time

# ======================
# MODAL
# ======================
class LoadingModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("🎤 Đang nhận diện")
        self.geometry("400x200")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        
        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        ctk.CTkLabel(self, text="🔴 Đang ghi âm...", 
                    font=("Arial", 20, "bold"),
                    text_color="#FF4444").pack(pady=30)
        
        self.progress = ctk.CTkProgressBar(self, width=300)
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        ctk.CTkLabel(self, text="Vui lòng nói nhận xét của bạn", 
                    font=("Arial", 14)).pack(pady=10)
        
        # Animation
        self.animate()
        
    
    def animate(self):
        try:
            val = self.progress.get()
            self.progress.set((val + 0.02) % 1.0)
            self.after(100, self.animate)
        except:
            pass


class VoiceModal(ctk.CTkToplevel):
    def __init__(self, parent, on_send):
        super().__init__(parent)

        self.title("🎤 Voice Comment")
        self.geometry("500x350")
        self.resizable(False, False)
        self.attributes('-topmost', True)

        self.on_send = on_send
        self.text_value = ""

        # Header
        header = ctk.CTkLabel(self, text="✓ Kết quả nhận diện", 
                             font=("Arial", 20, "bold"), 
                             text_color="#00D4FF")
        header.pack(pady=15)

        # Subtitle
        ctk.CTkLabel(self, text="Kiểm tra lại trước khi gửi", 
                    font=("Arial", 12),
                    text_color="#888888").pack(pady=5)

        # Text box
        self.textbox = ctk.CTkTextbox(self, width=450, height=130, 
                                      font=("Arial", 13),
                                      corner_radius=8)
        self.textbox.pack(pady=10, padx=20)

        self.protocol("WM_DELETE_WINDOW", self.close)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="✓ Gửi", 
                     command=self.send,
                     fg_color="#00D4FF",
                     hover_color="#00A8D4",
                     width=100,
                     font=("Arial", 12)).grid(row=0, column=0, padx=8)
        
        ctk.CTkButton(button_frame, text="✏️ Sửa", 
                     command=self.focus_edit,
                     fg_color="#FFA500",
                     hover_color="#FF8C00",
                     width=100,
                     font=("Arial", 12)).grid(row=0, column=1, padx=8)
        
        ctk.CTkButton(button_frame, text="🔄 Lại", 
                     command=self.redo,
                     fg_color="#9966FF",
                     hover_color="#7744DD",
                     width=100,
                     font=("Arial", 12)).grid(row=0, column=2, padx=8)
        
        ctk.CTkButton(button_frame, text="✕ Hủy", 
                     command=self.close,
                     fg_color="#FF4444",
                     hover_color="#DD3333",
                     width=100,
                     font=("Arial", 12)).grid(row=0, column=3, padx=8)

    def set_text(self, text):
        self.text_value = text
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

    def focus_edit(self):
        self.textbox.focus()

    def close(self):
        if hasattr(self.master, "current_voice_modal"):
            self.master.current_voice_modal = None
        super().destroy()

    def send(self):
        self.text_value = self.textbox.get("1.0", "end-1c")
        if self.text_value.strip():
            self.on_send(self.text_value)
        self.close()

    def redo(self):
        self.close()
        self.master.controller.is_listening = False
        time.sleep(0.3)
        threading.Thread(target=self.master.controller.voice_comment, args=(self.master,), daemon=True).start()


class VoiceError(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("⚠ Lỗi Giọng Nói")
        self.geometry("400x220")
        self.resizable(False, False)
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text="⚠ Không nhận diện được", 
                    font=("Arial", 18, "bold"),
                    text_color="#FF4444").pack(pady=20)

        ctk.CTkLabel(self, text="Vui lòng kiểm tra:\n• Microphone có hoạt động?\n• Nói rõ ràng hơn", 
                    font=("Arial", 13),
                    justify="left").pack(pady=15)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="🔄 Thử lại", 
                     command=self.retry,
                     fg_color="#FFA500",
                     width=120).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="✕ Đóng", 
                     command=self.destroy,
                     fg_color="#FF4444",
                     width=120).pack(side="left", padx=10)

    def retry(self):
        self.master.controller.is_listening = False
        self.destroy()
        time.sleep(0.3)
        threading.Thread(target=self.master.controller.voice_comment, args=(self.master,), daemon=True).start()
