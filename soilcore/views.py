from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import SoilType, UserProfile, SoilData, Newsletter, Device, Alert, SensorData
from django.utils import timezone
from collections import defaultdict


# ========================= HOME / ABOUT / TEMP =========================
def homepage(request):
    return render(request, 'home.html')

def aboutpage(request):
    return render(request, 'about.html')




# ========================= SOIL TYPES =========================
def soil_type_page(request):
    """Show all soil types with optional search by name."""
    query = request.GET.get("q", "")
    soil_types = SoilType.objects.filter(name__icontains=query) if query else SoilType.objects.all()
    return render(request, "soil_types.html", {"soil_types": soil_types, "query": query})



def add_soil_type(request):
    """Add a new soil type (logged-in users only)."""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        ph_min = request.POST.get("ph_min")
        ph_max = request.POST.get("ph_max")
        suitable_crops = request.POST.get("suitable_crops")
        location = request.POST.get("location")

        if name and description and ph_min and ph_max:
            SoilType.objects.create(
                name=name,
                description=description,
                ph_min=ph_min,
                ph_max=ph_max,
                suitable_crops=suitable_crops,
                location=location
            )
            messages.success(request, "✅ Soil type added successfully!")
            return redirect("soil_types")
        else:
            messages.error(request, "⚠️ Please fill in all required fields.")

    return render(request, "add_soil_type.html")


# ------------------- INLINE EDIT (AJAX) -------------------
@csrf_exempt
def edit_soil_type(request, id):
    """
    Handle inline edit via fetch/JS.
    Returns JSON {success: True/False}.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            soil = SoilType.objects.get(id=id)
            soil.name = data.get('name', soil.name)
            soil.description = data.get('description', soil.description)
            soil.ph_min = data.get('ph_min', soil.ph_min)
            soil.ph_max = data.get('ph_max', soil.ph_max)
            soil.suitable_crops = data.get('suitable_crops', soil.suitable_crops)
            soil.location = data.get('location', soil.location)
            soil.save()
            return JsonResponse({"success": True})
        except Exception as e:
            print("Edit error:", e)
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})


# ------------------- DELETE -------------------

def delete_soil_type(request, id):
    """
    Delete soil type (redirect after delete). If needed, can make AJAX delete too.
    """
    soil = get_object_or_404(SoilType, id=id)
    soil.delete()
    messages.success(request, "🗑️ Soil type deleted successfully!")
    return redirect("soil_types")


# ========================= LOGIN / SIGNUP =========================
def loginsignuppage(request):
    mode = request.GET.get('mode', 'login')

    # LOGIN
    if request.method == "POST" and "login_submit" in request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "✅ Logged in successfully!")
            next_url = request.GET.get("next", "dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "❌ Invalid username or password.")
            mode = "login"

    # SIGNUP
    elif request.method == "POST" and "signup_submit" in request.POST:
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        location = request.POST.get("location")
        agree_terms = request.POST.get("agreeTerms")

        if not agree_terms:
            messages.error(request, "⚠️ You must agree to Terms & Privacy Policy!")
            mode = "signup"
        elif password1 != password2:
            messages.error(request, "❌ Passwords do not match!")
            mode = "signup"
        elif User.objects.filter(username=username).exists():
            messages.error(request, "⚠️ Username already taken!")
            mode = "signup"
        else:
            user = User.objects.create_user(username=username, email=email, password=password1, first_name=full_name)
            UserProfile.objects.create(user=user, phone_number=phone_number, location=location)
            messages.success(request, "🎉 Account created! Please log in.")
            return redirect("login_signup")

    # FORGOT PASSWORD
    elif request.method == "POST" and "forgot_submit" in request.POST:
        email = request.POST.get("forgot_email")
        try:
            user = User.objects.get(email=email)
            messages.success(request, "📧 Password reset link sent to your email!")
        except User.DoesNotExist:
            messages.error(request, "❌ No account found with this email.")
        mode = "login"

    return render(request, "login_signup.html", {"mode": mode})


# ========================= LOGOUT =========================
def user_logout(request):
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect("login_signup")


# ========================= DASHBOARD =========================
# ========================= DASHBOARD =========================
@login_required(login_url="login_signup")
def dashboard(request):
    profile = getattr(request.user, 'userprofile', None)

    # Get latest SoilData for this user
    soil_data = SoilData.objects.filter(user=request.user).order_by('-updated_at').first()

    # Get last 7 readings
    soil_history = SoilData.objects.filter(user=request.user).order_by('-updated_at')[:7]
    soil_history = reversed(soil_history)

    # Prepare values for chart
    ph_values = [d.ph_level for d in soil_history]
    temp_values = [d.temperature for d in soil_history]
    humidity_values = [d.humidity for d in soil_history]
    timestamps = [d.updated_at.strftime("%H:%M") for d in soil_history]

    return render(request, "dashboard.html", {
        "profile": profile,
        "soil_data": soil_data,
        "ph_values": ph_values,
        "temp_values": temp_values,
        "humidity_values": humidity_values,
        "timestamps": timestamps,
    })

# ========================= PROFILE / SETTINGS =========================
def terms_privacy(request):
    return render(request, 'terms_privacy.html')

def profilepage(request):
    return render(request, 'profile.html')

# ========================= SETTINGS PAGE =========================
@login_required
def settingpage(request):
    profile = getattr(request.user, 'userprofile', None)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone_number", "").strip()
        location = request.POST.get("location", "").strip()

        # Update User
        if full_name:
            first_name, *last_name = full_name.split(" ", 1)
            request.user.first_name = first_name
            request.user.last_name = last_name[0] if last_name else ""
        if email:
            request.user.email = email
        request.user.save()

        # Update or create UserProfile
        if profile is None:
            profile = UserProfile.objects.create(user=request.user)
        profile.phone_number = phone
        profile.location = location
        profile.save()

        messages.success(request, "✅ Profile updated successfully!")

        return redirect('settingpage')  # reload the same page

    return render(request, 'settings.html', {"profile": profile})


# ========================= NEWSLETTER =========================
def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if Newsletter.objects.filter(email=email).exists():
                messages.error(request, "⚠️ This email is already subscribed.")
            else:
                Newsletter.objects.create(email=email)
                messages.success(request, "✅ Thank you for subscribing!")
        else:
            messages.error(request, "⚠️ Please enter a valid email.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

# =========================ph level =========================



# ------------------------------
# pH LEVEL DASHBOARD VIEW
# ------------------------------
@login_required
def ph_levels(request):
    """
    Render the pH Levels dashboard page.
    Displays chart, table, and live alerts.
    """
    devices = Device.objects.filter(user=request.user)
    # Default safe range (can be configurable later)
    safe_min = 6.0
    safe_max = 7.5

    context = {
        "devices": devices,
        "safe_min": safe_min,
        "safe_max": safe_max,
    }
    return render(request, "ph_levels.html", context)


# ------------------------------
# API ENDPOINT: FETCH LATEST pH DATA
# ------------------------------
@login_required
def api_ph_latest(request):
    """
    Returns JSON of latest pH readings for a given device.
    Used by JS (ph.js) for real-time chart updates.
    Example URL:
        /soilcore/api/ph/latest/?device_id=123&limit=50
    """
    device_id = request.GET.get("device_id")
    limit = int(request.GET.get("limit", 50))

    if not device_id:
        return JsonResponse({"error": "Missing device_id"}, status=400)

    try:
        device = Device.objects.get(id=device_id, user=request.user)
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)

    readings = (
        SoilData.objects.filter(device=device)
        .order_by("-timestamp")[:limit]
        .values("timestamp", "value")
    )

    data = list(readings)
    return JsonResponse({"readings": data})

# ------------------------------
# pH LEVELS PAGE
# ------------------------------
@login_required
def ph_levels(request):
    devices = Device.objects.filter(user=request.user)
    context = {
        "devices": devices,
        "thresholds": {"min": 6.0, "max": 7.5},  # for JS alert logic
    }
    return render(request, "ph_levels.html", context)


# ------------------------------
# FETCH LATEST DATA FOR CHART (used by JS)
# ------------------------------
@login_required
def api_ph_latest(request):
    device_id = request.GET.get("device_id")
    limit = int(request.GET.get("limit", 50))

    if not device_id:
        return JsonResponse({"error": "Missing device_id"}, status=400)

    try:
        device = Device.objects.get(id=device_id, user=request.user)
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found"}, status=404)

    readings = (
        SoilData.objects.filter(device=device)
        .order_by("-timestamp")[:limit]
        .values("timestamp", "value")
    )

    return JsonResponse({"readings": list(readings)})


# ------------------------------
# API ENDPOINT FOR IOT DEVICES TO PUSH DATA
# ------------------------------
@csrf_exempt
def api_iot_push(request):
    """
    API for IoT device to POST live pH readings.
    Example JSON:
    {
      "device_id": 1,
      "value": 6.7
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        device_id = data.get("device_id")
        value = data.get("value")

        # Validate
        if device_id is None or value is None:
            return JsonResponse({"error": "device_id and value required"}, status=400)

        device = Device.objects.get(id=device_id)
        SoilData.objects.create(device=device, value=value, timestamp=timezone.now())

        return JsonResponse({"status": "ok", "device": device_id, "value": value})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ========================= ALERTS =========================
# views.py
@login_required
def alerts_page(request):
    """
    Show all alerts for the logged-in user's devices.
    """
    user_devices = Device.objects.filter(user=request.user)
    alerts = Alert.objects.filter(device__in=user_devices).order_by('-timestamp')
    
    return render(request, 'alerts.html', {'alerts': alerts})


# ========================= LIVE DATA =========================
@login_required
def live_data(request):
    devices = Device.objects.filter(user=request.user)
    latest_readings = []
    for device in devices:
        latest = SoilData.objects.filter(device=device).order_by('-timestamp').first()
        if latest:
            latest_readings.append(latest)
    return render(request, 'live_data.html', {'latest_readings': latest_readings})


@login_required
def api_live_data(request):
    devices = Device.objects.filter(user=request.user)
    data = []
    for device in devices:
        latest = SoilData.objects.filter(device=device).order_by('-timestamp').first()
        if latest:
            data.append({
                'device_name': device.name,
                'value': latest.value,
                'timestamp': latest.timestamp.strftime("%H:%M:%S"),
            })
    return JsonResponse({'readings': data})

#crop advisor view



import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Device, SoilData, SoilType

@login_required
def crop_advisor(request):
    """
    Suggest crops based on latest pH readings from all user's devices.
    """
    devices = Device.objects.filter(user=request.user)
    recommendations = []

    for device in devices:
        # Get latest reading for this device
        latest_data = SoilData.objects.filter(device=device).order_by('-timestamp').first()
        if latest_data:
            ph = latest_data.value  # Assuming SoilData.value stores pH
            # Find suitable soils for this pH
            suitable_soils = SoilType.objects.filter(ph_min__lte=ph, ph_max__gte=ph)
            crops_set = set()
            for soil in suitable_soils:
                if soil.suitable_crops:
                    crops_set.update([c.strip() for c in soil.suitable_crops.split(",")])
            recommendations.append({
                "device": device,
                "ph": ph,
                "crops": list(crops_set),
                "timestamp": latest_data.timestamp
            })
        else:
            recommendations.append({
                "device": device,
                "ph": "No data",
                "crops": [],
                "timestamp": None
            })

    # Pass devices JSON for live JS updates
    devices_json = json.dumps([{"id": d.id, "name": d.name} for d in devices])

    return render(request, 'crop_advisor.html', {
        'recommendations': recommendations,
        'devices_json': devices_json
    })

# ========================== Soil Moisture View ==========================
@login_required
def soil_moisture(request):
    devices = Device.objects.filter(user=request.user)
    latest_data = {}
    chart_labels = []
    chart_values = []

    # Latest reading per device
    for device in devices:
        latest = SoilData.objects.filter(device=device).order_by('-updated_at').first()
        latest_data[device.id] = latest
        if latest:
            chart_labels.append(latest.updated_at.strftime("%H:%M %d-%m"))
            chart_values.append(float(latest.humidity or 0))

    # Last 10 readings across all devices
    recent_readings = SoilData.objects.filter(device__in=devices).order_by('-updated_at')[:10]

    context = {
        'devices': devices,
        'latest_data': latest_data,
        'recent_readings': recent_readings,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
    }
    return render(request, 'soil_moisture.html', context)

# ========================= TEMPERATURE PAGE =========================

@login_required
def temperaturepage(request):
    devices = Device.objects.filter(user=request.user)
    latest_data = {}
    
    # Latest data per device
    for device in devices:
        latest = SoilData.objects.filter(device=device).order_by('-updated_at').first()
        latest_data[device.id] = latest
    
    # Last 10 readings across all devices
    recent_readings = SoilData.objects.filter(device__in=devices).order_by('-updated_at')[:10]
    
    context = {
        'devices': devices,
        'latest_data': latest_data,
        'recent_readings': recent_readings,
    }
    return render(request, 'temperature.html', context)


# ========================= HUMIDITY PAGE =========================
@login_required
def humidity_page(request):
    devices = Device.objects.filter(user=request.user)
    latest_data = {}

    for device in devices:
        latest = SoilData.objects.filter(device=device).order_by('-updated_at').first()
        latest_data[device.id] = latest

    recent_readings = SoilData.objects.filter(device__in=devices).order_by('-updated_at')[:10]

    context = {
        'devices': devices,
        'latest_data': latest_data,
        'recent_readings': recent_readings,
    }
    return render(request, 'humidity.html', context)

############

from django.core.mail import send_mail
from django.contrib.auth.models import User

def send_test_email(request):
    user = request.user  # logged-in user
    send_mail(
        subject='Soil Alert!',
        message='This is a test alert message.',
        from_email='soilmonitor2025@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )
    return HttpResponse('Email sent!')
