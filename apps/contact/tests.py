from django.test import TestCase

from apps.contact.models import Inquiry


class InquiryModelTests(TestCase):

    def test_inquiry_str(self):
        inquiry = Inquiry.objects.create(
            name='John Smith',
            email='john@example.com',
            subject='Product availability',
            message='I would like to know more about your products.',
        )
        self.assertEqual(str(inquiry), 'John Smith — Product availability')

    def test_inquiry_is_unread_by_default(self):
        inquiry = Inquiry.objects.create(
            name='John Smith',
            email='john@example.com',
            subject='Product availability',
            message='I would like to know more about your products.',
        )
        self.assertFalse(inquiry.is_read)


class ContactFormSubmissionTests(TestCase):

    def test_valid_form_saves_to_db(self):
        response = self.client.post('/en/contact/', {
            'name': 'John Smith',
            'email': 'john@example.com',
            'subject': 'Product availability',
            'message': 'I would like to know more about your products.',
        })
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_valid_form_redirects(self):
        response = self.client.post('/en/contact/', {
            'name': 'John Smith',
            'email': 'john@example.com',
            'subject': 'Product availability',
            'message': 'I would like to know more about your products.',
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_form_does_not_save(self):
        self.client.post('/en/contact/', {
            'name': '',
            'email': 'not-an-email',
            'subject': '',
            'message': '',
        })
        self.assertEqual(Inquiry.objects.count(), 0)
