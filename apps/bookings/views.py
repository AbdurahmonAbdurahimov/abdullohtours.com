from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_ratelimit.decorators import ratelimit

from .forms import BookingRequestForm
from .models import BookingRequest


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def booking_request(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            obj: BookingRequest = form.save(commit=False)
            obj.source_type = BookingRequest.SourceType.DIRECT
            obj.save()
            # NOTE: enqueuing the Telegram "new request" Notification row
            # happens here in the full build (apps.notifications.senders);
            # left as a follow-up wire-up in this scaffold pass so the
            # booking flow itself is testable independent of the bot.
            return redirect(reverse("bookings:thanks", kwargs={"ref_code": obj.ref_code}))
    else:
        form = BookingRequestForm()
    return render(request, "bookings/booking_request.html", {"form": form})


def thanks(request: HttpRequest, ref_code: str) -> HttpResponse:
    obj = get_object_or_404(BookingRequest, ref_code=ref_code)
    return render(request, "bookings/thanks.html", {"booking": obj})


def ratelimited_view(request: HttpRequest, exception=None) -> HttpResponse:
    """settings.RATELIMIT_VIEW target — 5 requests/hour/IP on the booking form."""
    return HttpResponse(
        "Too many requests. Please try again later, or reach us directly on WhatsApp.",
        status=429,
    )
