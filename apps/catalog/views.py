from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Destination, Package


def destination_index(request: HttpRequest) -> HttpResponse:
    destinations = Destination.objects.filter(is_active=True)
    return render(request, "catalog/destination_index.html", {"destinations": destinations})


def destination_detail(request: HttpRequest, slug: str) -> HttpResponse:
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    return render(request, "catalog/destination_detail.html", {"destination": destination})


def package_index(request: HttpRequest) -> HttpResponse:
    packages = Package.objects.filter(is_active=True)
    return render(request, "catalog/package_index.html", {"packages": packages})


def package_detail(request: HttpRequest, slug: str) -> HttpResponse:
    package = get_object_or_404(Package, slug=slug, is_active=True)
    return render(request, "catalog/package_detail.html", {"package": package})


def tour_builder(request: HttpRequest) -> HttpResponse:
    """Step 1 of the 5-step tour builder (CLAUDE.md §6).

    Full Alpine.js/HTMX wiring is Phase 2 scope; this scaffold renders the
    page shell so the URL and template exist ahead of that work.
    """
    return render(request, "catalog/tour_builder.html")


@require_POST
def build_quote(request: HttpRequest) -> HttpResponse:
    """HTMX endpoint the builder POSTs the current selection to.

    Phase 2 will wire this to apps.catalog.pricing.calculate_quote() using
    the posted selection + a BuilderSession row. For now it returns a stub
    so the endpoint exists and the URL name is stable.
    """
    return JsonResponse(
        {
            "detail": "TODO: wire to apps.catalog.pricing.calculate_quote() in Phase 2 "
            "(Tour Builder).",
        },
        status=501,
    )
