from django.urls import path
from .views import BotGymView

urlpatterns = [
    path('preguntar/', BotGymView.as_view(), name='botgym_preguntar'),
]
