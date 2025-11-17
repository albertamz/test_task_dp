from django.urls import path
from app.views import tables, bookings

urlpatterns = [
    path("tables/", tables, name="tables"),
    path("bookings/", bookings, name="bookings"),
]
