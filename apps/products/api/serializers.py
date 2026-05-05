from rest_framework import serializers

from apps.products.models import Category, Certification, Application, Product


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'slug']


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'product_count']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    applications = ApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'cas_number',
            'e_number',
            'origin',
            'available_forms',
            'description',
            'specifications',
            'certifications',
            'applications',
            'meta_title',
            'meta_description',
        ]
