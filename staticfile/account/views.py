from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
import json, io, zipfile

from .models import UserProfile
from .forms import ProfilePicForm
# Optional: if you track soil readings per user
from soildata.models import DeviceReading

# -------------------------
# LOGIN / SIGNUP
# -------------------------
def loginsignuppage(request):
    mode = request.GET.get('mode', 'login')

    if request.method == "POST" and "login_submit" in request.POST:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "✅ Logged in successfully!")
            
            # Redirect safely to dashboard in soildata
            next_url = request.GET.get("next", None)
            if not next_url:
                next_url = "soildata:dashboard"
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
            # Create User and Profile
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=full_name
            )
            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                location=location
            )
            messages.success(request, "🎉 Account created! Please log in.")
            return redirect("account:login")

    elif request.method == "POST" and "forgot_submit" in request.POST:
        email = request.POST.get("forgot_email")
        try:
            user = User.objects.get(email=email)
            messages.success(request, "📧 Password reset link sent to your email!")
        except User.DoesNotExist:
            messages.error(request, "❌ No account found with this email.")
        mode = "login"

    return render(request, "login_signup.html", {"mode": mode})


# -------------------------
# LOGOUT
# -------------------------
def user_logout(request):
    logout(request)
    messages.info(request, "👋 You have been logged out.")
    return redirect("account:login")


# -------------------------
# PROFILE PAGE
# -------------------------
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import logout
from .models import UserProfile

from soildata.models import  DeviceReading
from .forms import ProfilePicForm  # your existing form

# -------------------------
# Profile page
# -------------------------
@login_required
def profilepage(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Profile picture upload
    if request.method == "POST" and request.FILES.get("profile_pic"):
        form = ProfilePicForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile picture updated!")
            return redirect('account:profilepage')

    # Latest soil readings
    readings = DeviceReading.objects.filter(device__user=user).order_by('-updated_at')[:10]

    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'readings': readings,
    })


# -------------------------
# AJAX: remove profile pic
# -------------------------
@login_required
def remove_profile_pic(request):
    if request.method == "POST":
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.profile_pic.delete(save=True)  # delete file from storage
        user_profile.profile_pic = None
        user_profile.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)


# -------------------------
# AJAX: update account info
# -------------------------
@login_required
def update_account_info(request):
    if request.method == "POST" and request.is_ajax():
        data = request.POST
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone_number", "").strip()
        location = data.get("location", "").strip()

        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Update full name
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        # Update email safely
        if email and email != user.email:
            from datetime import timedelta
            from django.utils import timezone
            can_change = True
            if profile.last_email_change:
                can_change = timezone.now() - profile.last_email_change >= timedelta(days=30)

            if can_change:
                user.email = email
                profile.last_email_change = timezone.now()
            else:
                return JsonResponse({"status": "error", "message": "❌ You can only change email once every 30 days."})

        user.save()

        # Update profile info
        profile.phone_number = phone
        profile.location = location
        profile.save()

        return JsonResponse({"status": "success", "message": "✅ Profile updated successfully!"})

    return JsonResponse({"status": "failed"}, status=400)


# -------------------------
# Optional: delete account
# -------------------------
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "🗑️ Your account and all data have been deleted.")
        return redirect("account:login")
    return redirect("account:profilepage")


# -------------------------
# SETTINGS PAGE
# -------------------------
@login_required
def settingpage(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    can_change_email = profile.can_change_email()

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone_number", "").strip()
        location = request.POST.get("location", "").strip()

        # Update full name
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        # Update email safely
        if email and email != user.email:
            if profile.update_email(email):
                messages.success(request, "✅ Email updated successfully!")
            else:
                messages.error(request, "❌ You can only change email once every 30 days.")
                return redirect("account:settingpage")

        user.save()
        profile.phone_number = phone
        profile.location = location
        profile.save()

        messages.success(request, "✅ Profile updated successfully!")
        return redirect("account:settingpage")

    return render(request, "settings.html", {
        "profile": profile,
        "can_change_email": can_change_email
    })


# -------------------------
# DOWNLOAD USER DATA
# -------------------------
from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def download_user_data(request):
    user = request.user
    profile = getattr(user, "userprofile", None)

    # PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    
    p.drawString(50, 800, f"User Profile for {user.username}")
    p.drawString(50, 780, f"Full Name: {user.first_name} {user.last_name}")
    p.drawString(50, 760, f"Email: {user.email}")
    p.drawString(50, 740, f"Phone: {profile.phone_number if profile else '-'}")
    p.drawString(50, 720, f"Location: {profile.location if profile else '-'}")

    p.drawString(50, 700, "Soil Readings:")
    readings = DeviceReading.objects.filter(device__user=user).order_by('-updated_at')
    y = 680
    for r in readings:
        p.drawString(60, y, f"{r.updated_at.strftime('%d-%m-%Y %H:%M')} - Moisture: {r.moisture}%")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response



# -------------------------
# DELETE ACCOUNT
# -------------------------
@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "🗑️ Your account and all associated data have been permanently deleted.")
        return redirect("account:login")
    return redirect("account:settingpage")
