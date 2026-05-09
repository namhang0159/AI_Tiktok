import customtkinter as ctk
import subprocess
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🚀 AI TikTok System")
        self.geometry("500x400")
        self.resizable(False, False)

        # Title
        ctk.CTkLabel(self, 
                     text="HỆ THỐNG AI TIKTOK", 
                     font=("Arial", 22, "bold")).pack(pady=30)

        # Buttons
        ctk.CTkButton(self, 
                      text="📸 Collect Data", 
                      width=250, height=50,
                      command=self.run_collect).pack(pady=15)

        ctk.CTkButton(self, 
                      text="🧠 Train Model", 
                      width=250, height=50,
                      command=self.run_train).pack(pady=15)

        ctk.CTkButton(self, 
                      text="🎬 Run AI TikTok", 
                      width=250, height=50,
                      fg_color="#00D4FF",
                      command=self.run_main).pack(pady=15)

        # Status
        self.status = ctk.CTkLabel(self, text="Ready...", font=("Arial", 12))
        self.status.pack(pady=20)

    def run_collect(self):
        self.run_script("collect_data.py")

    def run_train(self):
        self.run_script("train_model.py")

    def run_main(self):
        if not os.path.exists("model.pkl"):
            self.status.configure(text="❌ Chưa có model! Train trước!")
            return
        self.run_script("main.py")

    def run_script(self, script_name):
        try:
            self.status.configure(text=f"▶ Đang chạy {script_name}...")

            subprocess.Popen(["python", script_name])

        except Exception as e:
            self.status.configure(text=f"❌ Lỗi: {e}")

if __name__ == "__main__":
    app = Launcher()
    app.mainloop()