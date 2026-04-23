from django import forms

from .models import Inquiry


class InquiryForm(forms.ModelForm):

    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'company', 'phone', 'subject', 'product_interest', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name (optional)',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+66 xx xxx xxxx (optional)',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What is your inquiry about?',
            }),
            'product_interest': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your inquiry in detail…',
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'company': 'Company',
            'phone': 'Phone Number',
            'subject': 'Subject',
            'product_interest': 'Product of Interest',
            'message': 'Message',
        }
