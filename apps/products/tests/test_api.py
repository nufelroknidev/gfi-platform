from django.urls import reverse
from rest_framework.test import APITestCase

from apps.products.models import Category, Certification, Product


class ProductAPITests(APITestCase):

    def setUp(self):
        self.sweeteners = Category.objects.create(name='Sweeteners', slug='sweeteners')
        self.preservatives = Category.objects.create(name='Preservatives', slug='preservatives')

        self.halal = Certification.objects.create(name='Halal', slug='halal')

        self.stevia = Product.objects.create(
            category=self.sweeteners,
            name='Stevia Extract',
            slug='stevia-extract',
            cas_number='57817-89-7',
            is_active=True,
        )
        self.stevia.certifications.add(self.halal)

        self.sucralose = Product.objects.create(
            category=self.sweeteners,
            name='Sucralose',
            slug='sucralose',
            is_active=True,
        )

        self.inactive = Product.objects.create(
            category=self.preservatives,
            name='Hidden Product',
            slug='hidden-product',
            is_active=False,
        )

    def test_list_returns_200(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_excludes_inactive_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        names = [p['name'] for p in response.data['results']]
        self.assertNotIn('Hidden Product', names)
        self.assertEqual(len(names), 2)

    def test_detail_returns_200(self):
        url = reverse('product-detail', kwargs={'slug': 'stevia-extract'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Stevia Extract')

    def test_detail_unknown_slug_returns_404(self):
        url = reverse('product-detail', kwargs={'slug': 'does-not-exist'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_search_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Stevia'})
        self.assertEqual(response.status_code, 200)
        names = [p['name'] for p in response.data['results']]
        self.assertIn('Stevia Extract', names)
        self.assertNotIn('Sucralose', names)

    def test_search_by_cas_number(self):
        url = reverse('product-list')
        response = self.client.get(url, {'search': '57817-89-7'})
        names = [p['name'] for p in response.data['results']]
        self.assertIn('Stevia Extract', names)

    def test_category_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'category': 'sweeteners'})
        self.assertEqual(response.status_code, 200)
        names = [p['name'] for p in response.data['results']]
        self.assertIn('Stevia Extract', names)
        self.assertIn('Sucralose', names)

    def test_category_filter_excludes_other_categories(self):
        url = reverse('product-list')
        response = self.client.get(url, {'category': 'preservatives'})
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, [])

    def test_certification_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, {'certification': 'halal'})
        names = [p['name'] for p in response.data['results']]
        self.assertIn('Stevia Extract', names)
        self.assertNotIn('Sucralose', names)

    def test_detail_contains_expected_fields(self):
        url = reverse('product-detail', kwargs={'slug': 'stevia-extract'})
        response = self.client.get(url)
        for field in ['id', 'name', 'slug', 'category', 'certifications', 'applications',
                      'cas_number', 'e_number', 'origin', 'available_forms',
                      'description', 'specifications', 'meta_title', 'meta_description']:
            self.assertIn(field, response.data)
