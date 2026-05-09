from ultralytics import YOLO
import cv2
import mediapipe as mp
import os

class GenderDetector:
    def __init__(self):
        """Load YOLOv8 Gender Model"""

        # ======================
        # LOAD YOLO MODEL
        # ======================
        MODEL_PATH = "runs/classify/gender_model/weights/best.pt"

        if not os.path.exists(MODEL_PATH):
            raise Exception("❌ Chưa có runs/classify/gender_model/weights/best.pt")

        self.model = YOLO(MODEL_PATH)

        # ======================
        # MEDIAPIPE FACE DETECTION
        # ======================
        self.mp_face_detection = mp.solutions.face_detection

        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )

        # ======================
        # STABILITY
        # ======================
        self.last_gender = None
        self.stable_count = 0
        self.stability_threshold = 3

    # ======================
    # DETECT FACE
    # ======================
    def extract_face_from_frame(self, frame):

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.face_detector.process(img_rgb)

        if not results.detections:
            return None

        detection = results.detections[0]

        bbox = detection.location_data.relative_bounding_box

        h, w, c = frame.shape

        x_min = max(0, int(bbox.xmin * w))
        y_min = max(0, int(bbox.ymin * h))

        x_max = min(w, int((bbox.xmin + bbox.width) * w))
        y_max = min(h, int((bbox.ymin + bbox.height) * h))

        face_img = frame[y_min:y_max, x_min:x_max]

        if face_img.size == 0:
            return None

        return face_img, (x_min, y_min, x_max, y_max)

    # ======================
    # PREDICT GENDER
    # ======================
    def predict_gender(self, frame):
        """
        Detect và predict gender từ frame
        Return: (gender_label, gender_name, frame_with_bbox)
        """
        result = self.extract_face_from_frame(frame)

        if result is None:
            self.stable_count = 0
            return None, None, frame

        face_img, bbox = result

        # ======================
        # YOLO PREDICT
        # ======================
        results = self.model(face_img, verbose=False)

        probs = results[0].probs

        if probs is None:
            return None, None, frame

        gender_label = probs.top1
        confidence = probs.top1conf.item()

        # ======================
        # CONFIDENCE CHECK
        # ======================
        if confidence < 0.7:
            return None, None, frame

        gender_name = "Nữ (👩)" if gender_label == 0 else "Nam (🧑)"

        # ======================
        # STABILITY CHECK
        # ======================
        if gender_label == self.last_gender:
            self.stable_count += 1
        else:
            self.stable_count = 0
            self.last_gender = gender_label

        # ======================
        # DRAW
        # ======================
        frame_copy = frame.copy()

        x_min, y_min, x_max, y_max = bbox

        color = (255, 0, 0) if gender_label == 0 else (0, 255, 0)

        cv2.rectangle(
            frame_copy,
            (x_min, y_min),
            (x_max, y_max),
            color,
            2
        )

        cv2.putText(
            frame_copy,
            f"{gender_name} {confidence:.2f}",
            (x_min, y_min - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )

        # ======================
        # RETURN ONLY WHEN STABLE
        # ======================
        if self.stable_count >= self.stability_threshold:
            return gender_label, gender_name, frame_copy

        return None, None, frame_copy