from django import forms
from django.contrib import admin
from django.db.models import Count
from django.forms import widgets
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Application, Category, Certification, Product


class TagsWidget(widgets.HiddenInput):
    """Renders a comma-separated CharField as interactive pill tags in the admin."""

    class Media:
        css = {"all": ("css/admin/tags-widget.css",)}
        js = ("js/admin/tags-widget.js",)

    def render(self, name, value, attrs=None, renderer=None):
        hidden = super().render(name, value, attrs, renderer)
        return mark_safe(
            '<div class="tags-widget">'
            + hidden
            + '<div class="tags-list"></div>'
            '<div class="tags-input-row">'
            '<input type="text" class="tags-input" placeholder="Add a name…">'
            '<button type="button" class="tags-add-btn">+ Add</button>'
            "</div>"
            '<p class="help">Type a name and press Enter or click <strong>+ Add</strong>.</p>'
            "</div>"
        )


class SpecsTableWidget(widgets.Textarea):
    """Renders the pipe-separated specifications TextField as an editable table."""

    class Media:
        css = {"all": ("css/admin/specs-table-widget.css",)}
        js = ("js/admin/specs-table-widget.js",)

    def render(self, name, value, attrs=None, renderer=None):
        # Render as a hidden textarea so the value is submitted normally
        if attrs is None:
            attrs = {}
        attrs = {**attrs, "class": "specs-hidden", "style": "display:none"}
        textarea = super().render(name, value, attrs, renderer)
        return mark_safe(
            '<div class="specs-widget">'
            + textarea
            + '<div class="specs-table-wrap"></div>'
            '<div class="specs-table-actions">'
            '<button type="button" class="specs-add-row">+ Add Row</button>'
            "</div>"
            "</div>"
        )


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "alternative_names": TagsWidget(),
            "available_forms": TagsWidget(),
            "specifications": SpecsTableWidget(),
        }


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "product_count", "image_preview")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_product_count=Count("products"))

    def product_count(self, obj):
        return obj._product_count
    product_count.short_description = "Products"
    product_count.admin_order_field = "_product_count"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "origin", "is_active", "has_datasheet", "image_preview", "updated_at")
    list_filter = ("category", "is_active", "origin", "certifications", "applications")
    search_fields = ("name", "cas_number", "e_number", "alternative_names", "description")
    list_editable = ("is_active",)
    list_select_related = ("category",)
    save_on_top = True
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "image_preview")
    filter_horizontal = ("certifications", "applications")

    form = ProductAdminForm

    fieldsets = (
        ("Basic Info", {
            "fields": ("category", "name", "slug", "is_active"),
        }),
        ("Identification", {
            "description": "These fields are indexed for search. CAS numbers are commonly used by B2B buyers.",
            "fields": ("cas_number", "e_number", "alternative_names"),
        }),
        ("Content", {
            "fields": ("description", "specifications"),
        }),
        ("Classification", {
            "fields": ("origin", "available_forms", "certifications", "applications"),
        }),
        ("Media", {
            "fields": ("image", "image_preview", "datasheet"),
        }),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Image Preview"

    def has_datasheet(self, obj):
        return bool(obj.datasheet)
    has_datasheet.boolean = True
    has_datasheet.short_description = "TDS"
