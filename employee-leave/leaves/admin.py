from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "reason", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("employee__username", "reason")
