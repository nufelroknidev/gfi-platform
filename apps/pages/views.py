from django.shortcuts import render

from apps.products.models import Category, Product


def home(request):
    categories = Category.objects.all()
    # Six most recent active products — a featured flag can be added later.
    featured_products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .order_by('-created_at')[:6]
    )
    return render(request, 'pages/home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')
