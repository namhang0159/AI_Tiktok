# import os
# import shutil
# from pathlib import Path
# from ultralytics import YOLO

# # ======================
# # CẤU HÌNH
# # ======================
# IMG_SIZE = 224  # YOLOv8 nên dùng 224
# BATCH_SIZE = 16
# EPOCHS = 50
# CONFIDENCE = 0.5

# # Paths
# RAW_DATA_MALE = "dataset/male"
# RAW_DATA_FEMALE = "dataset/female"
# TRAIN_DIR = "dataset/yolo_data"

# # ======================
# # CHUẨN BỊ DỮ LIỆU
# # ======================
# print("🔄 Đang chuẩn bị dữ liệu YOLOv8...")

# # Xóa thư mục cũ nếu có
# if os.path.exists(TRAIN_DIR):
#     shutil.rmtree(TRAIN_DIR)

# # Tạo cấu trúc thư mục
# train_male = os.path.join(TRAIN_DIR, "train", "male")
# train_female = os.path.join(TRAIN_DIR, "train", "female")
# val_male = os.path.join(TRAIN_DIR, "val", "male")
# val_female = os.path.join(TRAIN_DIR, "val", "female")

# os.makedirs(train_male, exist_ok=True)
# os.makedirs(train_female, exist_ok=True)
# os.makedirs(val_male, exist_ok=True)
# os.makedirs(val_female, exist_ok=True)

# def split_data(src_folder, dst_train, dst_val, split_ratio=0.8):
#     """Chia dữ liệu 80% train, 20% val"""
#     files = [f for f in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, f))]
#     split_idx = int(len(files) * split_ratio)
    
#     print(f"📊 {src_folder}: {len(files)} ảnh (train: {split_idx}, val: {len(files)-split_idx})")
    
#     for i, file in enumerate(files):
#         src = os.path.join(src_folder, file)
#         dst = os.path.join(dst_train, file) if i < split_idx else os.path.join(dst_val, file)
        
#         try:
#             shutil.copy2(src, dst)
#         except Exception as e:
#             print(f"❌ Lỗi copy: {src}, {e}")
    
#     return len(files)

# # Sao chép dữ liệu
# male_count = split_data(RAW_DATA_MALE, train_male, val_male)
# female_count = split_data(RAW_DATA_FEMALE, train_female, val_female)

# print(f"✅ Tổng ảnh: {male_count + female_count}")

# # ======================
# # TẠO FILE CẤU HÌNH YAML
# # ======================
# yaml_content = f"""path: {os.path.abspath(TRAIN_DIR)}
# train: train
# val: val

# nc: 2
# names: ['male', 'female']
# """

# with open(os.path.join(TRAIN_DIR, "data.yaml"), "w") as f:
#     f.write(yaml_content)

# print("✅ Tạo file data.yaml")

# # ======================
# # LOAD & TRAIN YOLOv8
# # ======================
# print("🧠 Bắt đầu train YOLOv8...")

# # Load model (nano cho nhanh, small/medium/large nếu muốn chính xác hơn)
# model = YOLO("yolov8n-cls.pt")

# # Train
# results = model.train(
#     data=os.path.join(TRAIN_DIR, "data.yaml"),
#     epochs=EPOCHS,
#     imgsz=IMG_SIZE,
#     batch=BATCH_SIZE,
#     patience=10,  # Early stopping
#     device="cpu"  # GPU (nếu có)
#     project=".",
#     name="gender_model",
#     exist_ok=True,
#     verbose=True
# )

# print("✅ Train xong!")

# # ======================
# # SAVE & VALIDATE
# # ======================
# print("📊 Đang validate...")
# metrics = model.val()

# print(f"✅ Top1 Accuracy: {metrics.top1:.2%}")
# print(f"✅ Top5 Accuracy: {metrics.top5:.2%}")

# # Model đã được lưu tự động trong gender_model/weights/best.pt
# best_model_path = "gender_model/weights/best.pt"
# print(f"💾 Model đã lưu: {best_model_path}")

# # ======================
# # TEST (OPTIONAL)
# # ======================
# print("\n🧪 Test model...")
# model = YOLO(best_model_path)

# # Test với 1 ảnh
# test_image = os.path.join(RAW_DATA_FEMALE, os.listdir(RAW_DATA_FEMALE)[0])
# pred = model.predict(test_image, conf=CONFIDENCE)
# print(f"✅ Dự đoán: {pred[0].names[pred[0].probs.top1]}")

import os
import shutil
import random
from ultralytics import YOLO

# ======================
# CONFIG
# ======================
IMG_SIZE = 128
BATCH_SIZE = 8
EPOCHS = 30
CONFIDENCE = 0.5

RAW_DATA_MALE = "dataset/male"
RAW_DATA_FEMALE = "dataset/female"

TRAIN_DIR = "dataset/yolo_data"

# ======================
# PREPARE DATA
# ======================
print("🔄 Đang chuẩn bị dữ liệu YOLOv8...")

# Xóa folder cũ
if os.path.exists(TRAIN_DIR):
    shutil.rmtree(TRAIN_DIR)

# Tạo folder
folders = [
    "train/male",
    "train/female",
    "val/male",
    "val/female"
]

for folder in folders:
    os.makedirs(os.path.join(TRAIN_DIR, folder), exist_ok=True)

# ======================
# SPLIT DATA
# ======================
def split_data(src_folder, train_folder, val_folder, split_ratio=0.8):

    files = [
        f for f in os.listdir(src_folder)
        if os.path.isfile(os.path.join(src_folder, f))
    ]

    # RANDOM
    random.shuffle(files)

    split_idx = int(len(files) * split_ratio)

    print(
        f"📊 {src_folder}: "
        f"{len(files)} ảnh "
        f"(train: {split_idx}, val: {len(files)-split_idx})"
    )

    for i, file in enumerate(files):

        src = os.path.join(src_folder, file)

        if i < split_idx:
            dst = os.path.join(train_folder, file)
        else:
            dst = os.path.join(val_folder, file)

        try:
            shutil.copy2(src, dst)

        except Exception as e:
            print(f"❌ Lỗi copy {src}: {e}")

    return len(files)

# ======================
# COPY DATA
# ======================
male_count = split_data(
    RAW_DATA_MALE,
    os.path.join(TRAIN_DIR, "train/male"),
    os.path.join(TRAIN_DIR, "val/male")
)

female_count = split_data(
    RAW_DATA_FEMALE,
    os.path.join(TRAIN_DIR, "train/female"),
    os.path.join(TRAIN_DIR, "val/female")
)

print(f"✅ Tổng ảnh: {male_count + female_count}")

# ======================
# LOAD MODEL
# ======================
print("🧠 Loading YOLOv8 model...")

model = YOLO("yolov8n-cls.pt")

# ======================
# TRAIN
# ======================
print("🚀 Bắt đầu train...")

results = model.train(
    data=TRAIN_DIR,
    epochs=EPOCHS,
    imgsz=IMG_SIZE,
    batch=BATCH_SIZE,
    patience=10,
    device="cpu",
    project=".",
    name="gender_model",
    exist_ok=True,
    verbose=True
)

print("✅ Train xong!")

# ======================
# VALIDATE
# ======================
print("📊 Validate model...")

metrics = model.val()

if hasattr(metrics, "top1"):
    print(f"✅ Top1 Accuracy: {metrics.top1:.2%}")

if hasattr(metrics, "top5"):
    print(f"✅ Top5 Accuracy: {metrics.top5:.2%}")

# ======================
# BEST MODEL
# ======================
best_model_path = "gender_model/weights/best.pt"

print(f"💾 Best model: {best_model_path}")

# ======================
# TEST
# ======================
print("🧪 Test model...")

model = YOLO(best_model_path)

test_image = os.path.join(
    RAW_DATA_FEMALE,
    os.listdir(RAW_DATA_FEMALE)[0]
)

results = model.predict(
    source=test_image,
    conf=CONFIDENCE,
    verbose=False
)

probs = results[0].probs

label_id = probs.top1

label_name = results[0].names[label_id]

confidence = probs.top1conf.item()

print(
    f"✅ Predict: {label_name} "
    f"({confidence:.2%})"
)