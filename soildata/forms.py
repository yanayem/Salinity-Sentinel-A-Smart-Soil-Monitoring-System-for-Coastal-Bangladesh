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
