from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("destinations/", views.destination_index, name="destination_index"),
    path("destinations/<slug:slug>/", views.destination_detail, name="destination_detail"),
    path("tours/", views.package_index, name="package_index"),
    path("tours/<slug:slug>/", views.package_detail, name="package_detail"),
    path("routes/", views.route_index, name="route_index"),
    path("routes/<slug:slug>/", views.route_detail, name="route_detail"),
    path("hotels/", views.hotel_index, name="hotel_index"),
    path("hotels/<slug:slug>/", views.hotel_detail, name="hotel_detail"),
    path("cars/", views.car_index, name="car_index"),
    path("cars/<slug:slug>/", views.car_detail, name="car_detail"),
    path("build/", views.tour_builder, name="tour_builder"),
    path("build/quote/", views.build_quote, name="build_quote"),
    path("build/submit/", views.build_submit, name="build_submit"),
]
