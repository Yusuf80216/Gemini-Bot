from django.urls import path
from image_bot import views

urlpatterns = [
    path('image/', views.image_bot, name='image'),
]
