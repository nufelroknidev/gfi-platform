from django.shortcuts import render

from apps.products.models import Category, Product
from .models import HeroSlide


def home(request):
    categories = Category.objects.all()[:8]
    featured_products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .order_by('-created_at')[:8]
    )
    hero_slides = list(HeroSlide.objects.filter(is_active=True).order_by('order'))
    return render(request, 'pages/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'hero_slides': hero_slides,
    })


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')
