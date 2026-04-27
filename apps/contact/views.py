import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from .forms import InquiryForm

logger = logging.getLogger(__name__)


def inquiry(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            obj = form.save()
            if _send_auto_reply(obj):
                _notify_staff(obj)
            return redirect('contact:success')
    else:
        form = InquiryForm()
    return render(request, 'contact/inquiry.html', {'form': form})


def success(request):
    return render(request, 'contact/success.html')


def _send_auto_reply(obj):
    product_name = obj.product_interest.name if obj.product_interest else '—'
    context = {'name': obj.name, 'subject': obj.subject, 'product': product_name}
    try:
        EmailMessage(
            subject=render_to_string('contact/email/auto_reply_subject.txt').strip(),
            body=render_to_string('contact/email/auto_reply_body.txt', context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[obj.email],
            reply_to=[settings.CONTACT_EMAIL],
        ).send(fail_silently=False)
        return True
    except Exception:
        logger.exception(
            "Auto-reply failed for inquiry #%s — skipping staff notification", obj.pk
        )
        return False


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
        EmailMessage(
            subject=f"[GFI Inquiry] {obj.subject}",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[obj.email],
        ).send(fail_silently=False)
    except Exception:
        logger.exception(
            "Staff notification failed for inquiry #%s (%s)", obj.pk, obj.subject
        )
