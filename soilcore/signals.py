# soilcore/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Alert

@receiver(post_save, sender=Alert)
def send_alert_email(sender, instance, created, **kwargs):
    if created and not instance.emailed:
        user_email = instance.device.user.email
        subject = f"Alert: {instance.device.name} - {instance.parameter}"
        message = f"""
        Device: {instance.device.name}
        Parameter: {instance.parameter}
        Value: {instance.value}
        Type: {instance.threshold_type.upper()}
        Time: {instance.timestamp.strftime('%H:%M %d-%m-%Y')}
        """
        send_mail(
            subject,
            message,
            'no-reply@soilmonitor.com', 
            [user_email],
            fail_silently=True,
        )
    
        instance.emailed = True
        instance.save()
