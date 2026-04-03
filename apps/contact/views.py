import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import InquiryForm

logger = logging.getLogger(__name__)


def inquiry(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            _notify_staff(obj)
            return redirect('contact:success')
    else:
        form = InquiryForm()
    return render(request, 'contact/inquiry.html', {'form': form})


def success(request):
    return render(request, 'contact/success.html')


def _notify_staff(obj):
    product_name = obj.product_interest.name if obj.product_interest else '—'
    body = (
        f"New inquiry submitted via the GFI website.\n\n"
        f"Name:    {obj.name}\n"
        f"Email:   {obj.email}\n"
        f"Company: {obj.company or '—'}\n"
        f"Phone:   {obj.phone or '—'}\n"
        f"Product: {product_name}\n"
        f"Subject: {obj.subject}\n\n"
        f"Message:\n{obj.message}\n"
    )
    try:
        send_mail(
            subject=f"[GFI Inquiry] {obj.subject}",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Email notification failed for inquiry #%s (%s)", obj.pk, obj.subject
        )
