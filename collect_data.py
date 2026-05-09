import cv2
import mediapipe as mp
import numpy as np
import pickle
import customtkinter as ctk
from PIL import Image, ImageTk

# ======================
# SETUP
# ======================
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

data = []
labels = []

current_label = 0
collect = False

# label mapping cho dễ nhớ
label_names = {
    0: "Scroll",
    1: "Like ❤️",
    2: "Comment 💬",
    3: "Voice 🎤",
    4: "Send 📤"
}

# ======================
# UI
# ======================
class CollectApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Collect Data AI")
        self.geometry("1000x600")

        self.grid_columnconfigure(1, weight=1)

        # ===== Sidebar =====
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="COLLECT DATA", font=("Arial", 20, "bold")).pack(pady=20)

        # chọn label
        for i in range(5):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{i} - {label_names[i]}",
                command=lambda x=i: self.set_label(x)
            )
            btn.pack(pady=5)

        self.lbl_label = ctk.CTkLabel(self.sidebar, text="Label: 0")
        self.lbl_label.pack(pady=10)

        # start/stop
        self.btn_collect = ctk.CTkButton(self.sidebar, text="Start Collect", command=self.toggle_collect)
        self.btn_collect.pack(pady=10)

        # save
        self.btn_save = ctk.CTkButton(self.sidebar, text="Save Data", command=self.save_data)
        self.btn_save.pack(pady=10)

        # info
        self.lbl_samples = ctk.CTkLabel(self.sidebar, text="Samples: 0")
        self.lbl_samples.pack(pady=10)

        # ===== Video =====
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.lbl_video = ctk.CTkLabel(self.video_frame, text="")
        self.lbl_video.pack(expand=True, fill="both")

        self.update_frame()

    def set_label(self, label):
        global current_label
        current_label = label
        self.lbl_label.configure(text=f"Label: {label} - {label_names[label]}")

    def toggle_collect(self):
        global collect
        collect = not collect
        self.btn_collect.configure(text="Stop Collect" if collect else "Start Collect")

    def save_data(self):
        with open("data.pkl", "wb") as f:
            pickle.dump((data, labels), f)
        print("Saved data.pkl")

    def update_frame(self):
        global data, labels

        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    if collect:
                        # ===== NORMALIZE (RẤT QUAN TRỌNG)
                        base_x = hand_landmarks.landmark[0].x
                        base_y = hand_landmarks.landmark[0].y

                        lm_list = []
                        for lm in hand_landmarks.landmark:
                            lm_list.append(lm.x - base_x)
                            lm_list.append(lm.y - base_y)

                        data.append(lm_list)
                        labels.append(current_label)

            # UI info
            self.lbl_samples.configure(text=f"Samples: {len(data)}")

            # show cam
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.lbl_video.imgtk = imgtk
            self.lbl_video.configure(image=imgtk)

        self.after(20, self.update_frame)


# ======================
# RUN
# ======================
app = CollectApp()
app.mainloop()

cap.release()
cv2.destroyAllWindows()

