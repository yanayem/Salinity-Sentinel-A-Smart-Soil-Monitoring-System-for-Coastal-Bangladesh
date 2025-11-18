import os
import shutil
import random

BASE_DIR = "dataset"
CLASSES = ["Clay", "Sandy", "Silty", "Peaty", "Chalky", "Loamy"]

TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "val")

# Create train/val folders
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)

for cls in CLASSES:
    src = os.path.join(BASE_DIR, cls)
    train_dst = os.path.join(TRAIN_DIR, cls)
    val_dst = os.path.join(VAL_DIR, cls)

    os.makedirs(train_dst, exist_ok=True)
    os.makedirs(val_dst, exist_ok=True)

    if not os.path.exists(src):
        print(f"Missing folder: {src}")
        continue

    files = [f for f in os.listdir(src) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    random.shuffle(files)

    split_index = int(len(files) * 0.8)

    for f in files[:split_index]:
        shutil.copy(os.path.join(src, f), train_dst)

    for f in files[split_index:]:
        shutil.copy(os.path.join(src, f), val_dst)

print("Dataset split complete!")
