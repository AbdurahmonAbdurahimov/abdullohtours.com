from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("destinations/", views.destination_index, name="destination_index"),
    path("destinations/<slug:slug>/", views.destination_detail, name="destination_detail"),
    path("tours/", views.package_index, name="package_index"),
    path("tours/<slug:slug>/", views.package_detail, name="package_detail"),
    path("build/", views.tour_builder, name="tour_builder"),
    path("build/quote/", views.build_quote, name="build_quote"),
]
