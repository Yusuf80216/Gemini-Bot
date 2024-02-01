from django.urls import path
from pdf_chat import views

urlpatterns = [
    path('pdf/', views.pdf_chat, name='Chat with PDF'),
]
