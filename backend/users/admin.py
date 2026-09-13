from django.contrib import admin
from .models import PriceAlert

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "target_price", "active", "created_at")
    list_filter = ("active",)
