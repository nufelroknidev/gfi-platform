from django.db import models
from apps.utils.images import process_image


class SiteSettings(models.Model):
    phone = models.CharField(
        max_length=30,
        default="+66 2 000 1234",
        help_text="Phone number displayed in the top bar and contact page. Include country code, e.g. +66 2 000 1234",
    )
    phone_dialable = models.CharField(
        max_length=30,
        default="+6620001234",
        help_text="Phone number used for the tel: link (digits only, no spaces), e.g. +6620001234",
    )
    email = models.EmailField(
        default="info@gfi.co.th",
        help_text="Contact email displayed in the top bar and contact page.",
    )
    address = models.CharField(
        max_length=200,
        default="Bangkok, Thailand",
        help_text="Office address displayed in the footer and contact page.",
    )
    map_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Google Maps share link for the 'Get Directions' button (e.g. https://maps.google.com/?q=...). Use the Share → Copy link option in Google Maps.",
    )
    map_embed_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Google Maps embed URL for the map shown on the About page. In Google Maps, click Share → Embed a map → copy only the URL from the src=\"...\" part of the code.",
    )

    # Social media — leave blank to hide the icon from the website
    linkedin_url = models.URLField(max_length=500, blank=True, help_text="LinkedIn company page URL. Leave blank to hide.")
    facebook_url = models.URLField(max_length=500, blank=True, help_text="Facebook page URL. Leave blank to hide.")
    instagram_url = models.URLField(max_length=500, blank=True, help_text="Instagram profile URL. Leave blank to hide.")
    twitter_url = models.URLField(max_length=500, blank=True, help_text="X (Twitter) profile URL. Leave blank to hide.")
    youtube_url = models.URLField(max_length=500, blank=True, help_text="YouTube channel URL. Leave blank to hide.")
    tiktok_url = models.URLField(max_length=500, blank=True, help_text="TikTok profile URL. Leave blank to hide.")
    whatsapp_url = models.URLField(max_length=500, blank=True, help_text="WhatsApp Business link (e.g. https://wa.me/66812345678). Leave blank to hide.")
    line_url = models.URLField(max_length=500, blank=True, help_text="LINE Official Account URL or add-friend link. Leave blank to hide.")
    wechat_id = models.CharField(max_length=100, blank=True, help_text="WeChat Official Account ID. Leave blank to hide.")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @property
    def wechat_url(self):
        if not self.wechat_id:
            return None
        return f"https://weixin.qq.com/r/{self.wechat_id}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete("site_settings")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HeroSlide(models.Model):
    image = models.ImageField(
        upload_to="hero/",
        help_text="Recommended size: 1920 × 1080 px (16:9). Use a high-quality photo — it fills the full-width banner.",
    )
    alt_text = models.CharField(
        max_length=150,
        blank=True,
        help_text="Short description of the image for screen readers and SEO (e.g. 'Bulk food-grade citric acid powder').",
        verbose_name="Alt text",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order. Lower number = shown first. Drag-to-sort is not available — use whole numbers (1, 2, 3).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this slide without deleting it.",
        verbose_name="Active",
    )

    class Meta:
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"
        ordering = ["order"]

    def save(self, *args, **kwargs):
        process_image(self.image)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Slide {self.order}" + (f" — {self.alt_text}" if self.alt_text else "")


class SEOMixin(models.Model):
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Page title shown in search results (max 60 characters).",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Short description shown in search results (max 160 characters).",
    )

    class Meta:
        abstract = True
