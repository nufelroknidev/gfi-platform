from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Inquiry


class InquiryForm(forms.ModelForm):

    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'company', 'phone', 'subject', 'product_interest', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your full name'),
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('your@email.com'),
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company name (optional)'),
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('+66 xx xxx xxxx (optional)'),
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('What is your inquiry about?'),
            }),
            'product_interest': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Describe your inquiry in detail…'),
            }),
        }
        labels = {
            'name': _('Full Name'),
            'email': _('Email Address'),
            'company': _('Company'),
            'phone': _('Phone Number'),
            'subject': _('Subject'),
            'product_interest': _('Product of Interest'),
            'message': _('Message'),
        }
