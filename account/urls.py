from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.loginsignuppage, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profilepage, name='profilepage'),
    path('settings/', views.settingpage, name='settingpage'),
    path('download-data/', views.download_user_data, name='download_user_data'),
     path('profile/', views.profilepage, name='profilepage'),
    path('remove-profile-pic/', views.remove_profile_pic, name='remove_profile_pic'),
    path('update-account-info/', views.update_account_info, name='update_account_info'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('delete-account/', views.delete_account, name='delete_account'),
]
