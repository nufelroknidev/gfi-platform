from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.pages.models import SEOMixin
from apps.utils.images import process_image


class Post(SEOMixin):
    title = models.CharField(max_length=200, help_text="News post headline.")
    slug = models.SlugField(max_length=220, unique=True, help_text="URL-friendly identifier. Auto-generated from title.")
    content = models.TextField(help_text="Full post body. Supports rich text formatting.")
    featured_image = models.ImageField(upload_to="news/", blank=True, null=True, help_text="Header image for this post.")
    published_date = models.DateField(default=timezone.now, help_text="Date shown as the publication date.")
    is_published = models.BooleanField(default=False, db_index=True, help_text="Check to make this post visible on the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        process_image(self.featured_image)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', args=[self.slug])
