from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import SoilType, UserProfile, Newsletter

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


# ========================= LOGIN / SIGNUP =========================
def loginsignuppage(request):
    mode = request.GET.get('mode', 'login')

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
            return redirect("login")

    elif request.method == "POST" and "forgot_submit" in request.POST:
        email = request.POST.get("forgot_email")
        try:
            user = User.objects.get(email=email)
            messages.success(request, "📧 Password reset link sent to your email!")
        except User.DoesNotExist:
            messages.error(request, "❌ No account found with this email.")
        mode = "login"

    return render(request, "login_signup.html", {"mode": mode})

def user_logout(request):
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect("login")


# ========================= DASHBOARD =========================
@login_required(login_url="login")
def dashboard(request):
    profile = getattr(request.user, 'userprofile', None)
    return render(request, "dashboard.html", {"profile": profile})


# ========================= PROFILE / SETTINGS =========================
def terms_privacy(request):
    return render(request, 'terms_privacy.html')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, SoilReading
from .forms import ProfilePicForm
from django.http import JsonResponse

@login_required
def profilepage(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Handle profile picture upload
    if request.method == "POST":
        form = ProfilePicForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profilepage')
    
    # Latest soil readings for this user (latest per field)
    readings = SoilReading.objects.filter(user=user).order_by('-created_at')[:10]

    context = {
        'user': user,
        'profile': profile,
        'readings': readings,
    }
    return render(request, 'profile.html', context)

# API endpoint for real-time data (AJAX)
@login_required
def soil_data_api(request):
    user = request.user
    readings = SoilReading.objects.filter(user=user).order_by('-created_at')[:5]
    data = [
        {
            'field': r.field_name,
            'ph': r.ph,
            'moisture': r.moisture,
            'temperature': r.temperature,
            'time': r.created_at.strftime("%H:%M:%S")
        } for r in readings
    ]
    return JsonResponse({'readings': data})


import json, io, zipfile
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import UserProfile, SoilReading


@login_required
def settingpage(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    can_change_email = True
    if profile.last_email_change and timezone.now() - profile.last_email_change < timedelta(days=30):
        can_change_email = False

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone_number", "").strip()
        location = request.POST.get("location", "").strip()

        # Full name
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        # Email (once per 30 days)
        if email and email != user.email:
            if can_change_email:
                user.email = email
                profile.last_email_change = timezone.now()
            else:
                messages.error(request, "❌ You can only change your email once every 30 days.")
                return redirect("settingpage")

        user.save()

        profile.phone_number = phone
        profile.location = location
        profile.save()

        messages.success(request, "✅ Profile updated successfully!")
        return redirect("settingpage")

    return render(request, "settings.html", {"profile": profile, "can_change_email": can_change_email})


# 🧾 DOWNLOAD ALL USER DATA
@login_required
def download_user_data(request):
    user = request.user
    profile = getattr(user, "userprofile", None)

    # Prepare data separately
    user_data = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.isoformat(),
    }

    profile_data = {
        "phone_number": profile.phone_number if profile else "",
        "location": profile.location if profile else "",
    }

    soil_readings_data = list(SoilReading.objects.filter(user=user).values())

    # Create ZIP file dynamically
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("user.json", json.dumps(user_data, indent=2))
        zf.writestr("profile.json", json.dumps(profile_data, indent=2))
        zf.writestr("soil_readings.json", json.dumps(soil_readings_data, indent=2))

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{user.username}_data.zip"'
    return response

# 🗑️ DELETE ACCOUNT SAFELY
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "🗑️ Your account and all associated data have been permanently deleted.")
        return redirect("login")
    return redirect("settingpage")

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
