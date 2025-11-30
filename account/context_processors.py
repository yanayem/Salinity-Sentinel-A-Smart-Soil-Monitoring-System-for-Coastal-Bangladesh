from .models import UserProfile

def global_profile(request):
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = None
    else:
        profile = None

    return {
        'global_profile': profile
    }
