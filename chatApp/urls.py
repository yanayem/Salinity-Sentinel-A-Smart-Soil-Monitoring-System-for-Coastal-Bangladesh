from django.urls import path
from .views import chat_view

urlpatterns = [
    path('', chat_view, name='chat_new'),            # For new chat session
    path('<int:session_id>/', chat_view, name='chat'),  # For existing session
]
