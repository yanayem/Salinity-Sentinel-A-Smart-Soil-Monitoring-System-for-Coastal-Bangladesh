from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


from .models import SoilType, UserProfile, SoilData, Newsletter


# ========================= HOME / ABOUT / TEMP =========================
def homepage(request):
    return render(request, 'home.html')

def aboutpage(request):
    return render(request, 'about.html')

def temperature(request):
    return render(request, 'temperature.html')


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
@login_required(login_url="login_signup")
def dashboard(request):
    profile = getattr(request.user, 'userprofile', None)
    soil_data = SoilData.objects.filter(user=request.user).order_by('-updated_at').first()
    soil_type = soil_data.soil_type if soil_data else None
    soil_history = SoilData.objects.filter(user=request.user).order_by('-updated_at')[:7]
    soil_history = reversed(soil_history)
    ph_values = [d.ph_level for d in soil_history]
    temp_values = [d.temperature for d in soil_history]
    humidity_values = [d.humidity for d in soil_history]
    timestamps = [d.updated_at.strftime("%H:%M") for d in soil_history]

    return render(request, "dashboard.html", {
        "profile": profile,
        "soil_data": soil_data,
        "soil_type": soil_type,
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

def settingpage(request):
    return render(request, 'settings.html')


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
