from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("request/", views.booking_request, name="booking_request"),
    path("request/<str:ref_code>/thanks/", views.thanks, name="thanks"),
]
