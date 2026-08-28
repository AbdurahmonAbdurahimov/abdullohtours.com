from django import forms

from .models import BookingRequest


class BookingRequestForm(forms.ModelForm):
    """Short booking request form (CLAUDE.md §6): "keep it short" — only
    name, email, WhatsApp/phone, country, optional message. Every extra
    field costs conversion, so resist adding more here.

    Spam protection: a honeypot field (`website`) that must stay empty —
    real visitors never see or fill it (hidden via CSS in the template) —
    plus `django-ratelimit` (5/hour/IP) applied on the view. No visible
    CAPTCHA per spec.
    """

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
        label="",
        help_text="Leave this field empty.",
    )

    class Meta:
        model = BookingRequest
        fields = ["full_name", "email", "phone", "whatsapp", "country", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_website(self) -> str:
        value = self.cleaned_data.get("website", "")
        if value:
            # Bots fill every field; a non-empty honeypot means "reject
            # silently" — raise here so form_valid() never proceeds.
            raise forms.ValidationError("Spam detected.")
        return value
