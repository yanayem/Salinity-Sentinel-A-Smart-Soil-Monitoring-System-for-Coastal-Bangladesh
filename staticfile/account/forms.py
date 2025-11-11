from django import forms
from .models import UserProfile

class ProfilePicForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']
