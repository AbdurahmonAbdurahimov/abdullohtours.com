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

    # Widgets carry no CSS of their own out of the box, which left every
    # field rendering as an unstyled browser default input (dark-grey box,
    # no border) instead of the design system's input treatment used
    # everywhere else (e.g. the tour builder's date inputs). Applied here,
    # once, rather than per-field in the template.
    INPUT_CLASS = "w-full border border-hairline rounded px-3 py-2 bg-surface-raised text-content placeholder:text-content-muted focus:outline-none focus:border-gold-bright"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "website":
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {self.INPUT_CLASS}".strip()

    def clean_website(self) -> str:
        value = self.cleaned_data.get("website", "")
        if value:
            # Bots fill every field; a non-empty honeypot means "reject
            # silently" — raise here so form_valid() never proceeds.
            raise forms.ValidationError("Spam detected.")
        return value
