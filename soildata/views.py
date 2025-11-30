from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Device, DeviceReading
from account.models import UserProfile
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Device, DeviceReading
from django.http import JsonResponse
from soilcore.models import SoilType



# -------------------------
# Dashboard view
# -------------------------
import json

@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Latest 7 moisture readings
    readings = list(
        DeviceReading.objects.filter(device__user=user)
        .order_by('-updated_at')[:7]
    )

    # For Chart.js (reverse to show oldest -> newest)
    readings_chart = readings[::-1]

    chart_labels = json.dumps([r.updated_at.strftime("%H:%M") for r in readings[::-1]])
    chart_data = json.dumps([r.moisture for r in readings[::-1]])

    return render(request, "dashboard.html", {
        "user": user,
        "profile": profile,
        "readings": readings[::-1],  
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
    recommendations = []
    tips = []
    ph_value = None
    soil_type_input = ""
    location_input = ""

    if request.method == "POST":
        ph_raw = request.POST.get("ph")
        soil_type_input = request.POST.get("soil_type", "").strip()
        location_input = request.POST.get("location", "").strip()

        try:
            ph_value = float(ph_raw)
        except (ValueError, TypeError):
            ph_value = None

        if ph_value is not None:
            soils = SoilType.objects.filter(ph_min__lte=ph_value, ph_max__gte=ph_value)

            if soil_type_input:
                soils = soils.filter(name__icontains=soil_type_input)

            if location_input:
                soils = soils.filter(location__icontains=location_input)

            for soil in soils:
                if soil.suitable_crops:
                    crops_list = [c.strip() for c in soil.suitable_crops.split(",")]
                    recommendations.extend(crops_list)

                if soil.description:
                    tips.append(soil.description)

            recommendations = list(set(recommendations))
            tips = list(set(tips))

    context = {
        "recommendations": recommendations,
        "tips": tips,
        "ph_value": ph_value,
        "soil_type_input": soil_type_input,
        "location_input": location_input,
    }
    return render(request, "crop_advisor.html", context)

