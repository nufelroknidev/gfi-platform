from django.contrib import admin

from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "subject", "submitted_at", "is_read")
    list_filter = ("is_read",)
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject")
    readonly_fields = (
        "name", "email", "company", "phone",
        "subject", "message", "product_interest", "submitted_at",
    )

    fieldsets = (
        ("Contact Details", {
            "fields": ("name", "email", "company", "phone"),
        }),
        ("Inquiry", {
            "fields": ("subject", "message", "product_interest"),
        }),
        ("Status", {
            "fields": ("is_read", "submitted_at"),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
