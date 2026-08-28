from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.http import require_GET

from apps.catalog.models import Destination

from .models import Review


def home(request: HttpRequest) -> HttpResponse:
    destinations = Destination.objects.filter(is_active=True)[:5]
    return render(request, "core/home.html", {"destinations": destinations})


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
