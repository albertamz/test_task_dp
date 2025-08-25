from django.urls import path
from app.views import booking

urlpatterns = [
    path("", booking),
]
