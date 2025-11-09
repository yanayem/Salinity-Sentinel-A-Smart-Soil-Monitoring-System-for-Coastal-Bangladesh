import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Device, DeviceReading, SoilType, Alert, SoilData


from django import forms
from .models import Device

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'device_id', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded p-2', 'placeholder': 'Device Name'}),
            'device_id': forms.TextInput(attrs={'class': 'border rounded p-2', 'placeholder': 'Device ID'}),
            'location': forms.TextInput(attrs={'class': 'border rounded p-2', 'placeholder': 'Location'}),
        }

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Device
from .forms import DeviceForm
import uuid

@login_required
def devices(request):
    devices = Device.objects.filter(user=request.user).order_by('-is_active', 'name')
    form = DeviceForm()
    return render(request, 'devices.html', {'devices': devices, 'form': form})


@login_required
def activate_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.is_active = True  # just activate this one
    device.save()
    return redirect('soildata:devices')

@login_required
def deactivate_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.is_active = False
    device.save()
    return redirect('soildata:devices')

@login_required
def toggle_device_status(request):
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        device = get_object_or_404(Device, id=device_id, user=request.user)
        device.is_active = not device.is_active
        device.save()
        return JsonResponse({
            'success': True,
            'is_active': device.is_active
        })
    return JsonResponse({'success': False}, status=400)
@login_required
def add_device(request):
    auto_device_id = str(uuid.uuid4())[:8]  # Auto-generate ID
    success = False

    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.user = request.user
            device.save()
            success = True
            return redirect('soildata:devices')  # redirect to devices list
    else:
        form = DeviceForm(initial={'device_id': auto_device_id})

    return render(request, 'add_device.html', {'form': form, 'success': success})
    

@login_required
def activate_device(request, device_id):
    # Deactivate all devices
    Device.objects.filter(user=request.user).update(is_active=False)
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.is_active = True
    device.save()
    return redirect('soildata:devices')


@login_required
def remove_device(request, device_id):
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.delete()
    return redirect('soildata:devices')

# ------------------------------
# 🌱 Soil Moisture Dashboard
# ------------------------------
@login_required
def soil_moisture(request):
    devices = Device.objects.filter(user=request.user)
    device_id = request.GET.get('device_id')
    selected_device = devices.first() if devices.exists() else None
    latest_data = None
    recent_readings = []
    chart_labels, chart_values = [], []

    if selected_device and device_id:
        selected_device = get_object_or_404(devices, id=device_id)

    if selected_device:
        recent_readings = DeviceReading.objects.filter(device=selected_device).order_by('-updated_at')[:10]
        latest_data = recent_readings.first()
        chart_labels = [r.updated_at.strftime("%H:%M") for r in reversed(recent_readings)]
        chart_values = [r.humidity for r in reversed(recent_readings)]

    context = {
        'devices': devices,
        'selected_device': selected_device,
        'latest_data': latest_data,
        'recent_readings': recent_readings,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
    }
    return render(request, 'soil_moisture.html', context)


# ------------------------------
# ➕ Add Device
# ------------------------------
@login_required
def add_device(request):
    success = False
    error = None

    if request.method == 'POST':
        name = request.POST.get('name')
        device_id = request.POST.get('device_id')
        location = request.POST.get('location')

        if name and device_id and location:
            if Device.objects.filter(device_id=device_id).exists():
                error = "Device ID already exists! Please choose a different one."
            else:
                Device.objects.create(
                    user=request.user,
                    name=name,
                    device_id=device_id,
                    location=location,
                    is_active=False
                )
                success = True

    return render(request, 'add_device.html', {
        'success': success,
        'error': error
    })

# ------------------------------
# 📡 API: IoT Push Data
# ------------------------------
@csrf_exempt
def api_iot_push(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        device_id = data.get('device_id')
        moisture = data.get('moisture')
        ph = data.get('ph')
        temp = data.get('temperature')

        device = Device.objects.get(id=device_id)
        DeviceReading.objects.create(device=device, humidity=moisture, ph_level=ph, temperature=temp)
        return JsonResponse({'status': 'success'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ------------------------------
# 🔄 Live Data API
# ------------------------------
@login_required
def api_live_data(request):
    device_id = request.GET.get('device_id')
    default_response = {'humidity': 60, 'ph_level': 6.8, 'temperature': 25, 'timestamp': '--:-- --/--/----'}

    if not device_id:
        return JsonResponse(default_response)

    try:
        device = Device.objects.get(id=device_id, user=request.user)
        latest = DeviceReading.objects.filter(device=device).order_by('-updated_at').first()
        if latest:
            return JsonResponse({
                'humidity': latest.humidity,
                'ph_level': latest.ph_level,
                'temperature': latest.temperature,
                'timestamp': latest.updated_at.strftime("%H:%M:%S %d-%m-%Y")
            })
        return JsonResponse(default_response)
    except Device.DoesNotExist:
        return JsonResponse({'error': 'Invalid device'}, status=404)


# ------------------------------
# 🌡 Temperature Page
# ------------------------------
@login_required
def temperature_page(request):
    devices = Device.objects.filter(user=request.user, is_active=True)
    latest_data = {
        d.id: DeviceReading.objects.filter(device=d).order_by('-updated_at').first()
        for d in devices
    }
    return render(request, 'temperature.html', {
        'devices': devices,
        'latest_data': latest_data
    })


@login_required
def api_device_readings(request):
    """Return JSON with all active device readings."""
    devices = Device.objects.filter(user=request.user, is_active=True)
    data = []
    for d in devices:
        latest = DeviceReading.objects.filter(device=d).order_by('-updated_at').first()
        if latest:
            data.append({
                'id': d.id,
                'name': d.name,
                'temperature': latest.temperature,
            })
    return JsonResponse({'devices': data})


# ------------------------------
# 💧 Humidity Page
# ------------------------------
from django.utils import timezone

@login_required
def humidity_page(request):
    devices = Device.objects.filter(user=request.user)
    latest_data = {d.id: DeviceReading.objects.filter(device=d).order_by('-updated_at').first() for d in devices}
    
    context = {
        'devices': devices,
        'latest_data': latest_data,
        'current_time': timezone.now()
    }
    return render(request, 'humidity.html', context)


# ------------------------------
# ⚖ pH Levels Page
# ------------------------------
@login_required
def ph_levels(request):
    devices = Device.objects.filter(user=request.user)
    return render(request, 'ph_levels.html', {'devices': devices, 'thresholds': {'min': 6.0, 'max': 7.5}})


from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except:
        return 0

# ------------------------------
# API ENDPOINT: Latest pH Data
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

    readings = SoilData.objects.filter(device=device).order_by("-timestamp")[:limit].values("timestamp", "value")
    return JsonResponse({"readings": list(readings)})


# ------------------------------
# 📊 Crop Advisor
# ------------------------------
@login_required
def crop_advisor(request):
    devices = Device.objects.filter(user=request.user)
    recommendations = []

    for device in devices:
        latest = DeviceReading.objects.filter(device=device).order_by('-updated_at').first()
        if latest and latest.ph_level is not None:
            soils = SoilType.objects.filter(ph_min__lte=latest.ph_level, ph_max__gte=latest.ph_level)
            crops = set()
            for soil in soils:
                if soil.suitable_crops:
                    crops.update([c.strip() for c in soil.suitable_crops.split(",")])
            recommendations.append({'device': device, 'ph': latest.ph_level, 'crops': list(crops), 'timestamp': latest.updated_at})
        else:
            recommendations.append({'device': device, 'ph': 'No data', 'crops': [], 'timestamp': None})

    return render(request, 'crop_advisor.html', {'recommendations': recommendations})


# ------------------------------
# 🚨 Alerts Page
# ------------------------------
@login_required
def alerts_page(request):
    devices = Device.objects.filter(user=request.user)
    alerts = Alert.objects.filter(device__in=devices).order_by('-timestamp')
    return render(request, 'alerts.html', {'alerts': alerts})


# ------------------------------
# 🌍 Live Data Page
# ------------------------------
from django.shortcuts import render
from .models import Device
from django.utils import timezone

def live_data_page(request):
    # Get only active devices for the current user
    devices = Device.objects.filter(user=request.user, is_active=True).prefetch_related('readings')
    
    context = {
        'devices': devices
    }
    return render(request, 'live_data.html', context)

# ------------------------------
# 🌾 Soil Data API (last 5 readings)
# ------------------------------
@login_required
def soil_data_api(request):
    user = request.user
    readings = DeviceReading.objects.filter(device__user=user).order_by('-updated_at')[:5]
    data = [{
        'field': r.device.name,
        'ph': r.ph_level,
        'moisture': r.humidity,
        'temperature': r.temperature,
        'time': r.updated_at.strftime("%H:%M:%S")
    } for r in readings]
    return JsonResponse({'readings': data})


# ------------------------------
# ➕ Devices Management (Add/List/Activate/Remove)
# ------------------------------
from django import forms

# Form for adding a device
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'location']  # assuming your model has location
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded p-2 flex-1', 'placeholder': 'Device Name'}),
            'location': forms.TextInput(attrs={'class': 'border rounded p-2 flex-1', 'placeholder': 'Device Location'}),
        }

@login_required
def devices(request):
    """Show all devices, handle adding new device"""
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.user = request.user
            device.save()
            return redirect('soildata:devices')
    else:
        form = DeviceForm()

    devices = Device.objects.filter(user=request.user)
    return render(request, 'devices.html', {'devices': devices, 'form': form})


@login_required
def activate_device(request, device_id):
    """Activate the selected device and deactivate others"""
    # Deactivate all devices for this user
    Device.objects.filter(user=request.user).update(is_active=False)
    
    # Activate selected device
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.is_active = True
    device.save()
    
    return redirect('soildata:devices')


@login_required
def remove_device(request, device_id):
    """Remove selected device"""
    device = get_object_or_404(Device, id=device_id, user=request.user)
    device.delete()
    return redirect('soildata:devices')



import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Device

@login_required
@csrf_exempt
def add_device_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        location = data.get('location')
        if name and location:
            device_id = str(uuid.uuid4())[:8]
            device = Device.objects.create(
                user=request.user,
                name=name,
                location=location,
                device_id=device_id,
                is_active=False
            )
            return JsonResponse({
                'status': 'success',
                'device': {
                    'id': device.id,
                    'name': device.name,
                    'location': device.location,
                    'device_id': device.device_id,
                    'is_active': device.is_active
                }
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

from django.shortcuts import render
from .models import Device

def alerts_page(request):
    devices = Device.objects.prefetch_related('alerts').filter(is_active=True)
    return render(request, 'alerts.html', {'devices': devices})
