from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/list.html', {'categories': categories})


def product_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    all_categories = Category.objects.all()
    products = (
        Product.objects
        .filter(category=category, is_active=True)
        .select_related('category')
    )

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q)

    context = {
        'category':       category,
        'all_categories': all_categories,
        'products':       products,
        'q':              q,
    }

    if request.headers.get('X-GFI-Partial'):
        return render(request, 'products/_products_grid.html', context)

    return render(request, 'products/category.html', context)


def product_search(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if q:
        products = (
            Product.objects
            .filter(is_active=True)
            .filter(Q(name__icontains=q) | Q(description__icontains=q))
            .select_related('category')
            .order_by('name')
        )
    return render(request, 'products/search.html', {'products': products, 'q': q})


def product_detail(request, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(Product, slug=slug, category=category, is_active=True)
    return render(request, 'products/detail.html', {
        'product':  product,
        'category': category,
    })
