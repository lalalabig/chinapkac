from django.contrib import admin
from .models import EmergencyAlert

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('sender', 'location_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('sender__username', 'location_address')
