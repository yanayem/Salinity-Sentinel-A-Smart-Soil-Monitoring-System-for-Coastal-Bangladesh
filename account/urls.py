from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

app_name = 'account'

urlpatterns = [
    # -------------------
    # Login / Logout
    # -------------------
    path('login/', views.loginsignuppage, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # -------------------
    # Password Reset
    # -------------------
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # -------------------
    # Profile / Settings
    # -------------------
    path('profile/', views.profilepage, name='profilepage'),
    path('settings/', views.settingpage, name='settingpage'),

    # -------------------
    # Other account actions
    # -------------------
    path('download-data/', views.download_user_data, name='download_user_data'),
    path('ajax-upload-profile-pic/', views.ajax_upload_profile_pic, name='ajax_upload_profile_pic'),
    path('remove-profile-pic/', views.remove_profile_pic, name='remove_profile_pic'),
    path('update-account-info/', views.update_account_info, name='update_account_info'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
