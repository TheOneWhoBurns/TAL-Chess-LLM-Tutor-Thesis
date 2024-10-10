

from django.urls import path
from . import views  # Add this import statement

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chess-tutor/', views.chess_tutor_api, name='chess_tutor_api'),
]
