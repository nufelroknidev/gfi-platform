from django.db import models


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

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


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
