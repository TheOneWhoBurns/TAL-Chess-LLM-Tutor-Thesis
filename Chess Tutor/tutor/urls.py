
from django.urls import path
from . import views

urlpatterns = [
    path('api/chess-tutor/', views.chess_tutor, name='chess_tutor'),
]
