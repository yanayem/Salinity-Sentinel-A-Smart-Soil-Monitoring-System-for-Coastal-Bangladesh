from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import SoilType, Newsletter
from account.models import UserProfile 

# ========================= HOME / ABOUT =========================
def homepage(request):
    return render(request, 'home.html')

def aboutpage(request):
    return render(request, 'about.html')


# ========================= SOIL TYPES =========================
def soil_type_page(request):
    query = request.GET.get("q", "")
    soil_types = SoilType.objects.filter(name__icontains=query) if query else SoilType.objects.all()
    return render(request, "soil_types.html", {"soil_types": soil_types, "query": query})

def add_soil_type(request):
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

@csrf_exempt
def edit_soil_type(request, id):
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

def delete_soil_type(request, id):
    soil = get_object_or_404(SoilType, id=id)
    soil.delete()
    messages.success(request, "🗑️ Soil type deleted successfully!")
    return redirect("soil_types")


# ========================= PROFILE / SETTINGS =========================
def terms_privacy(request):
    return render(request, 'terms_privacy.html')


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
