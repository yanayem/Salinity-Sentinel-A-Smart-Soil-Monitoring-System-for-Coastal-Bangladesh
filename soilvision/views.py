from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SoilPrediction
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from sklearn.preprocessing import LabelEncoder
import numpy as np
from django.contrib.auth.decorators import login_required
from io import BytesIO

# Load model and label encoder once
MODEL_PATH = 'soilvision/soil_cnn_model.h5'
LABEL_PATH = 'soilvision/label_encoder_classes.npy'
model = load_model(MODEL_PATH)

label_encoder = LabelEncoder()
label_encoder.classes_ = np.load(LABEL_PATH, allow_pickle=True)

@login_required
def soil_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        try:
            # Convert uploaded file to BytesIO
            img_bytes = BytesIO(uploaded_file.read())
            img = load_img(img_bytes, target_size=(150, 150))
            img_array = img_to_array(img)
            img_array = img_array.reshape((1,) + img_array.shape)
            img_array /= 255.0

            # Make prediction
            predictions = model.predict(img_array)
            predicted_class = label_encoder.inverse_transform([np.argmax(predictions)])[0]
            confidence = float(np.max(predictions)) * 100

            # Save prediction to DB
            soil_pred = SoilPrediction.objects.create(
                user=request.user,
                image=uploaded_file,  
                predicted_soil_type=predicted_class,
                confidence=confidence
            )

            messages.success(request, f"Predicted Soil Type: {predicted_class} ({confidence:.2f}%)")
            return render(request, 'soil_upload.html', {'prediction': soil_pred})

        except Exception as e:
            messages.error(request, f"Error processing image: {e}")
            return redirect('soilvision:soil_upload')  

    return render(request, 'soil_upload.html')

@login_required
def soil_history(request):
    history = SoilPrediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "soil_history.html", {"history": history})
