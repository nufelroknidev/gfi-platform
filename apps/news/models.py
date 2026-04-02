from django.db import models
from django.utils import timezone

from apps.pages.models import SEOMixin


class Post(SEOMixin):
    title = models.CharField(max_length=200, help_text="News post headline.")
    slug = models.SlugField(max_length=220, unique=True, help_text="URL-friendly identifier. Auto-generated from title.")
    content = models.TextField(help_text="Full post body. Rich-text editor will be added in the admin phase.")
    featured_image = models.ImageField(upload_to="news/", blank=True, null=True, help_text="Header image for this post.")
    published_date = models.DateField(default=timezone.now, help_text="Date shown as the publication date.")
    is_published = models.BooleanField(default=False, help_text="Check to make this post visible on the website.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:detail', args=[self.slug])
