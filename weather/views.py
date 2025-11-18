from django.shortcuts import render
from django.contrib import messages
import requests
import datetime
import random

def weatherpage(request):
    city = request.POST.get('city', 'Indore')

    # OpenWeather API
    OPENWEATHER_API_KEY = '963804a07802e5371e2a2bd19f6a7afb'
    weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric'

    # Unsplash API
    UNSPLASH_ACCESS_KEY = '1p8c8r_JXHlH5-CStbJgX5JNheF7_7YanrgSftDbZX8'
    unsplash_url = f'https://api.unsplash.com/photos/random?query={city}&orientation=landscape&client_id={UNSPLASH_ACCESS_KEY}'

    # Default values
    temp = 25
    humidity = 50
    rain = 0
    description = 'clear sky'
    icon = '01d'
    image_url = '/static/media/Untitled.png'
    exception_occurred = False

    # Fetch city image from Unsplash
    try:
        data_img = requests.get(unsplash_url).json()
        image_url = data_img['urls']['regular']
    except:
        image_url = '/static/media/Untitled.png'

    # Fetch weather data
    try:
        data = requests.get(weather_url).json()
        if data.get('cod') == 200:
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            description = data['weather'][0]['description']
            icon = data['weather'][0]['icon']
            rain = data.get('rain', {}).get('1h', 0)
        else:
            exception_occurred = True
            messages.error(request, 'City not found in Weather API')
    except:
        exception_occurred = True
        messages.error(request, 'Error fetching Weather API')

    # Generate rain drops
    rain_drops = [random.randint(0, 100) for _ in range(50)]
    day = datetime.date.today()

    context = {
        'city': city,
        'temp': temp,
        'humidity': humidity,
        'rain': rain,
        'description': description,
        'icon': icon,
        'day': day,
        'image_url': image_url,
        'exception_occurred': exception_occurred,
        'rain_drops': rain_drops,
    }

    return render(request, 'weather.html', context)
