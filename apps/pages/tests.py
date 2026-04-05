from django.test import TestCase


class URLResolutionTests(TestCase):

    def test_home_page(self):
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)

    def test_about_page(self):
        response = self.client.get('/en/about/')
        self.assertEqual(response.status_code, 200)

    def test_services_page(self):
        response = self.client.get('/en/services/')
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get('/en/contact/')
        self.assertEqual(response.status_code, 200)

    def test_news_page(self):
        response = self.client.get('/en/news/')
        self.assertEqual(response.status_code, 200)

    def test_products_page(self):
        response = self.client.get('/en/products/')
        self.assertEqual(response.status_code, 200)

    def test_admin_requires_login(self):
        response = self.client.get('/en/admin/')
        self.assertEqual(response.status_code, 302)
