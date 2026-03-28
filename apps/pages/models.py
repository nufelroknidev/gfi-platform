from django.db import models


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
