import django_filters
from django.db.models import Count
from rest_framework import viewsets, mixins

from apps.products.models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    certification = django_filters.CharFilter(field_name='certifications__slug', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['category', 'certification']


class ProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['name', 'cas_number', 'e_number', 'alternative_names', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related('category')
            .prefetch_related('certifications', 'applications')
        )


class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products'))
