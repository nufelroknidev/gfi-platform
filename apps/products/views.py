from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/list.html', {'categories': categories})


def product_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    all_categories = Category.objects.all()
    products = Product.objects.filter(category=category, is_active=True)

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q)

    return render(request, 'products/category.html', {
        'category': category,
        'all_categories': all_categories,
        'products': products,
        'q': q,
    })


def product_detail(request, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=slug, category=category, is_active=True)
    return render(request, 'products/detail.html', {
        'product': product,
        'category': category,
    })
