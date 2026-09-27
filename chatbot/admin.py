from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'keywords', 'is_active')
    search_fields = ('question', 'keywords', 'answer')
    