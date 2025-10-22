# soilcore/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SoilType, UserProfile,SoilData,Newsletter  # ✅ fixed imports


# ---------------- HOME / ABOUT ----------------
def homepage(request):
    return render(request, 'home.html')

def aboutpage(request):
    return render(request, 'about.html')

def temperature(request):
    return render(request, 'temperature.html')


# soilcore/views.py
def soil_type_page(request):
    query = request.GET.get("q", "")
    if query:
        soil_types = SoilType.objects.filter(name__icontains=query)
    else:
        soil_types = SoilType.objects.all()
    return render(request, "soil_types.html", {"soil_types": soil_types, "query": query})


# ---------------- LOGIN / SIGNUP / FORGOT PASSWORD ----------------
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UserProfile

def loginsignuppage(request):
    mode = request.GET.get('mode', 'login')

    # ---------------- LOGIN ----------------
    if request.method == "POST" and "login_submit" in request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "✅ Logged in successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "❌ Invalid username or password.")
            mode = "login"

    # ---------------- SIGNUP ----------------
    elif request.method == "POST" and "signup_submit" in request.POST:
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        location = request.POST.get("location")
        agree_terms = request.POST.get("agreeTerms")  # checkbox

        # Validate Terms & Conditions
        if not agree_terms:
            messages.error(request, "⚠️ You must agree to the Terms & Privacy policy!")
            mode = "signup"

        # Password match validation
        elif password1 != password2:
            messages.error(request, "❌ Passwords do not match!")
            mode = "signup"

        # Username uniqueness
        elif User.objects.filter(username=username).exists():
            messages.error(request, "⚠️ Username already taken!")
            mode = "signup"

        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=full_name
            )
            UserProfile.objects.create(user=user, phone_number=phone_number, location=location)
            messages.success(request, "🎉 Account created successfully! Please log in.")
            return redirect("login_signup")

    # ---------------- FORGOT PASSWORD ----------------
    elif request.method == "POST" and "forgot_submit" in request.POST:
        email = request.POST.get("forgot_email")
        try:
            user = User.objects.get(email=email)
            # Here you can send reset link via email using Django's PasswordResetForm or custom email logic
            messages.success(request, "📧 Password reset link has been sent to your email!")
        except User.DoesNotExist:
            messages.error(request, "❌ No account found with this email.")
        mode = "login"  # redirect to login after forgot password attempt

    return render(request, "login_signup.html", {"mode": mode})



# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect("login_signup")


# ---------------- DASHBOARD ----------------
@login_required(login_url="login_signup")
def dashboard(request):
    profile = getattr(request.user, 'userprofile', None)

    # Latest soil data for cards
    soil_data = SoilData.objects.filter(user=request.user).order_by('-updated_at').first()
    soil_type = soil_data.soil_type if soil_data else None

    # Last 7 readings for graphs
    soil_history = SoilData.objects.filter(user=request.user).order_by('-updated_at')[:7]
    soil_history = reversed(soil_history)  # oldest first

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
def terms_privacy(request):
    return render(request, 'terms_privacy.html')

def profilepage(request):
    return render(request, 'profile.html')

def settingpage(request):
    return render(request, 'settings.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if Newsletter.objects.filter(email=email).exists():
                messages.error(request, "This email is already subscribed.")
            else:
                Newsletter.objects.create(email=email)
                messages.success(request, "Thank you for subscribing to our newsletter!")
        else:
            messages.error(request, "Please enter a valid email.")
    return redirect(request.META.get('HTTP_REFERER', '/'))