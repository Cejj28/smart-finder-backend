from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'item_name', 'location', 'reporter', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('item_name', 'location', 'description')
