from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.http import require_GET

from apps.catalog.models import Destination, Package

from .models import Review


def home(request: HttpRequest) -> HttpResponse:
    destinations = list(Destination.objects.filter(is_active=True)[:5])
    # The hero uses the first destination that actually has an image as its
    # backdrop; with no images seeded yet this stays None and the template
    # falls back to the navy gradient rather than rendering an empty frame.
    hero_destination = next((d for d in destinations if d.hero_image), None)
    featured_packages = list(
        Package.objects.filter(is_active=True, is_featured=True).select_related("base_vehicle_class")[:3]
    )
    # Real aggregate over published reviews only (apps/core/models.py Review
    # docstring: this app ships with zero seeded rows, so this is None/0
    # until an admin publishes real reviews — never a fabricated figure).
    review_stats = Review.objects.filter(is_published=True).aggregate(
        avg_rating=Avg("rating"), count=Count("id")
    )
    if review_stats["avg_rating"] is not None:
        review_stats["star_range"] = range(round(review_stats["avg_rating"]))
    return render(
        request,
        "core/home.html",
        {
            "destinations": destinations,
            "hero_destination": hero_destination,
            "featured_packages": featured_packages,
            "review_stats": review_stats,
        },
    )


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "core/about.html")


def reviews(request: HttpRequest) -> HttpResponse:
    reviews_qs = Review.objects.filter(is_published=True).select_related("package", "destination")
    return render(request, "core/reviews.html", {"reviews": reviews_qs})


def faq(request: HttpRequest) -> HttpResponse:
    return render(request, "core/faq.html")


def contact(request: HttpRequest) -> HttpResponse:
    return render(request, "core/contact.html")


@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("core/robots.txt")
    return HttpResponse(template.render({}, request), content_type="text/plain")
