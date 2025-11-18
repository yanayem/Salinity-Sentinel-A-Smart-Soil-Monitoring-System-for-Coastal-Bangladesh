import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing import image
from PIL import Image
import requests
from io import BytesIO

SOIL_CLASSES = ["Clay", "Sandy", "Silty", "Peaty", "Chalky", "Loamy"]

def create_model(input_shape=(128,128,3), num_classes=6):
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
        MaxPooling2D(2,2),
        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D(2,2),
        Conv2D(128, (3,3), activation='relu'),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def predict_image(model, img_path=None, img_url=None, target_size=(128,128)):
    if img_url:
        response = requests.get(img_url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = img.resize(target_size)
    elif img_path:
        img = image.load_img(img_path, target_size=target_size)
    else:
        raise ValueError("Provide img_path or img_url")

    x = image.img_to_array(img)/255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x)
    class_index = np.argmax(pred)
    confidence = float(np.max(pred))*100
    return {"soil_type": SOIL_CLASSES[class_index], "confidence": round(confidence,2)}
