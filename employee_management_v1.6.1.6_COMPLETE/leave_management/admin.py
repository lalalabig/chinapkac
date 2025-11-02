from django.contrib import admin
from .models import LeaveApplication


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'leave_start_date', 'leave_end_date', 'status', 'application_date')
    list_filter = ('status', 'application_date')
    search_fields = ('applicant__username', 'place')
    ordering = ('-application_date',)
