from django.urls import path
from . import views

urlpatterns = [
     path('', views.index, name='index'),  # Ensure this is the home page
    path('chatbot/get-response/', views.chatbot_response, name='chatbot_response')
]
