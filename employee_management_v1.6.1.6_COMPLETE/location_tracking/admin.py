from django.contrib import admin
from .models import LocationRecord

@admin.register(LocationRecord)
class LocationRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'location_name', 'latitude', 'longitude', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'location_name')
