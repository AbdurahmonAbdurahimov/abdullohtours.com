from django.urls import path

from . import telegram_bot

app_name = "notifications"

urlpatterns = [
    path("tg/webhook/<str:secret>/", telegram_bot.telegram_webhook, name="telegram_webhook"),
]
