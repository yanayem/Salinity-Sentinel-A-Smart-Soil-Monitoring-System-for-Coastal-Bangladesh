
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Set the path to your main dataset directory
main_dataset_dir = 'C:/Users/ADMIN/Desktop/Soil_Water_Analysis_Application/dataset/Soil types'

# Load data and labels
data = []
labels = []

# Define the target image size
target_size = (150, 150)

# Iterate over subdirectories (each subdirectory represents a soil type)
for soil_type in os.listdir(main_dataset_dir):
    soil_type_path = os.path.join(main_dataset_dir, soil_type)
    
    # Check if it's a directory
    if os.path.isdir(soil_type_path):
        
        # Iterate over images in the subdirectory
        for image_file in os.listdir(soil_type_path):
            image_path = os.path.join(soil_type_path, image_file)
            
            # Check if it's an image file (adjust extensions if needed)
            if image_path.endswith((".jpg", ".jpeg", ".png")):
                # Load and resize the image
                img = load_img(image_path, target_size=target_size)
                img_array = img_to_array(img)
                
                # Append the image array and label to the lists
                data.append(img_array)
                labels.append(soil_type)

# Convert data and labels to NumPy arrays
data = np.array(data)
labels = np.array(labels)

# Encode categorical labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(data, encoded_labels, test_size=0.2, random_state=42)

# Data augmentation for the training set
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow(X_train, y_train, batch_size=32)

model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(len(np.unique(encoded_labels)), activation='softmax'))  # Adjust the number of classes dynamically

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
history = model.fit(train_generator, epochs=10, validation_data=(X_test, y_test))

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f'Test accuracy: {test_acc}')

# Save the trained model and LabelEncoder using pickle
with open('soil_cnn_model.pkl', 'wb') as f:
    pickle.dump((model, label_encoder), f)
