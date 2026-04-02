from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.news.models import Post
from apps.products.models import Product


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return [
            'pages:home',
            'pages:about',
            'pages:services',
            'contact:inquiry',
            'products:list',
            'news:list',
        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def lastmod(self, obj):
        return obj.updated_at


class NewsSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
