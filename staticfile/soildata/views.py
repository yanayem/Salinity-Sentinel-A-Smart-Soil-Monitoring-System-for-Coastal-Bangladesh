from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Device, DeviceReading
from account.models import UserProfile
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Device, DeviceReading
from django.http import JsonResponse



# -------------------------
# Dashboard view
# -------------------------
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Latest 10 moisture readings
    readings = DeviceReading.objects.filter(device__user=user).order_by('-updated_at')[:10]

    # For Chart.js (reverse to show oldest -> newest)
    readings_chart = readings[::-1]

    chart_labels = [r.updated_at.strftime("%H:%M") for r in readings_chart]
    chart_data = [r.moisture for r in readings_chart]

    return render(request, "dashboard.html", {
        "user": user,
        "profile": profile,
        "readings": readings,
        "chart_labels": chart_labels,
        "chart_data": chart_data
    })

# -------------------------
# Soil Moisture view
# -------------------------
@login_required
def soil_moisture(request):
    device = Device.objects.filter(user=request.user, is_active=True).first()
    if device:
        readings = DeviceReading.objects.filter(device=device).order_by('-updated_at')[:50]
        # Convert updated_at to localtime in view
        for r in readings:
            r.local_time = timezone.localtime(r.updated_at)
    else:
        readings = []
    return render(request, "soil_moisture.html", {"readings": readings})

# -------------------------
# API to get moisture data
# -------------------------

@login_required
def api_moisture(request):
    device = Device.objects.filter(user=request.user, is_active=True).first()
    readings = []
    if device:
        qs = DeviceReading.objects.filter(device=device).order_by('-updated_at')[:50]
        for r in qs:
            readings.append({
                "time": timezone.localtime(r.updated_at).strftime("%I:%M %p %d-%m-%Y"),
                "moisture": r.moisture
            })

    latest = readings[0] if readings else {"time": "--", "moisture": 0}
    return JsonResponse({"latest": latest, "readings": readings})

# -------------------------
# Alerts view
# -------------------------

@login_required
def alerts(request):
    device = Device.objects.filter(user=request.user, is_active=True).first()
    MIN_MOISTURE = 20
    MAX_MOISTURE = 80
    alert_list = []

    if device:
        readings = DeviceReading.objects.filter(device=device).order_by('-updated_at')[:50]
        for r in readings:
            local_time = timezone.localtime(r.updated_at).strftime("%I:%M %p %d-%m-%Y")
            if r.moisture < MIN_MOISTURE:
                alert_list.append({
                    "time": local_time,
                    "moisture": r.moisture,
                    "type": "Low Moisture",
                    "message": f"Soil moisture is too low ({r.moisture}%)"
                })
            elif r.moisture > MAX_MOISTURE:
                alert_list.append({
                    "time": local_time,
                    "moisture": r.moisture,
                    "type": "High Moisture",
                    "message": f"Soil moisture is too high ({r.moisture}%)"
                })

    if request.GET.get("ajax"):
        return HttpResponse(render_to_string("alerts_content.html", {"alerts": alert_list}))

    return render(request, "alerts.html", {"alerts": alert_list})

# -------------------------
# Crop Advisor view
# -------------------------

@login_required
def crop_advisor(request):
    device = Device.objects.filter(user=request.user, is_active=True).first()
    suggestion = None
    moisture = None

    if device:
        reading = DeviceReading.objects.filter(device=device).order_by('-updated_at').first()
        if reading:
            moisture = reading.moisture
            if moisture <= 30:
                suggestion = ["Cactus 🌵", "Aloe Vera 🌿", "Millet 🌾"]
            elif 31 <= moisture <= 60:
                suggestion = ["Wheat 🌾", "Corn 🌽", "Tomato 🍅"]
            elif 61 <= moisture <= 80:
                suggestion = ["Rice 🌾", "Sugarcane 🍬", "Banana 🍌"]
            else:
                suggestion = ["Water Lily 🌸", "Taro 🌿", "Bamboo 🎋"]
    
    return render(request, "crop_advisor.html", {
        "moisture": moisture,
        "suggestion": suggestion,
    })
