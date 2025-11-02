from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('uploader', 'report_type', 'upload_date')
    list_filter = ('report_type', 'upload_date')
    search_fields = ('uploader__username',)
