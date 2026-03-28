from django.db import models


class Inquiry(models.Model):
    name = models.CharField(max_length=100, help_text="Full name of the person submitting the inquiry.")
    email = models.EmailField(help_text="Contact email address.")
    company = models.CharField(max_length=150, blank=True, help_text="Company or organisation name (optional).")
    phone = models.CharField(max_length=30, blank=True, help_text="Phone number including country code (optional).")
    subject = models.CharField(max_length=200, help_text="Brief subject of the inquiry.")
    message = models.TextField(help_text="Full inquiry message.")
    product_interest = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
        help_text="Product this inquiry relates to (optional).",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, help_text="Mark as read once the inquiry has been reviewed.")

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.name} — {self.subject}"
