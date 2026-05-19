from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import HeroSlide, SiteSettings


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("preview_thumb", "order", "alt_text", "is_active")
    list_display_links = ("preview_thumb", "alt_text")
    list_editable = ("order", "is_active")
    list_per_page = 10
    save_on_top = True

    fields = ("image", "preview_thumb", "alt_text", "order", "is_active")
    readonly_fields = ("preview_thumb",)

    def preview_thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; width:107px; object-fit:cover; border-radius:4px;">',
                obj.image.url,
            )
        return "—"
    preview_thumb.short_description = "Preview"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contact Information", {
            "fields": ("phone", "phone_dialable", "email"),
            "description": "These values appear in the top bar and on the contact page.",
        }),
        ("Location", {
            "fields": ("address", "map_url", "map_embed_url"),
            "description": (
                "Address appears in the footer. "
                "'Map URL' is the share link for the Get Directions button. "
                "'Map embed URL' is the src URL for the embedded map on the About page "
                "(Google Maps → Share → Embed a map → copy the URL from src=\"...\")."
            ),
        }),
        ("Social Media", {
            "fields": ("linkedin_url", "facebook_url", "instagram_url", "twitter_url", "youtube_url", "tiktok_url", "whatsapp_url", "line_url", "wechat_id"),
            "description": "Leave a field blank to hide that icon from the website.",
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        change_url = reverse("admin:pages_sitesettings_change", args=[obj.pk])
        return HttpResponseRedirect(change_url)
