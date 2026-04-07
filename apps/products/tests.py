from django.test import TestCase

from apps.products.models import Category, Product


class CategoryModelTests(TestCase):

    def test_category_str(self):
        category = Category.objects.create(name='Sweeteners', slug='sweeteners')
        self.assertEqual(str(category), 'Sweeteners')

    def test_category_requires_name(self):
        category = Category(slug='no-name')
        with self.assertRaises(Exception):
            category.full_clean()


class ProductModelTests(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Sweeteners', slug='sweeteners')

    def test_product_str(self):
        product = Product.objects.create(
            category=self.category,
            name='Stevia Extract',
            slug='stevia-extract',
        )
        self.assertEqual(str(product), 'Stevia Extract')

    def test_product_get_absolute_url(self):
        product = Product.objects.create(
            category=self.category,
            name='Stevia Extract',
            slug='stevia-extract',
        )
        self.assertEqual(product.get_absolute_url(), '/en/products/sweeteners/stevia-extract/')

    def test_product_inactive_by_default_is_active(self):
        product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
        )
        self.assertTrue(product.is_active)
