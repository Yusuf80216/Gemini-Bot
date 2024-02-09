from django.urls import path
from text_bot import views

urlpatterns = [
    path('chat/', views.generate_text, name='generate_text'),
]
