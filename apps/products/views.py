import json

from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from .models import Application, Category, Certification, Product, ORIGIN_CHOICES

PRODUCTS_PER_PAGE = 12

# Full-text search is available on PostgreSQL only.
try:
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
    _PG_SEARCH_AVAILABLE = True
except ImportError:
    _PG_SEARCH_AVAILABLE = False


def _pg_search_active():
    return _PG_SEARCH_AVAILABLE and connection.vendor == 'postgresql'


def _search_products(queryset, q):
    """Apply keyword search, using PostgreSQL FTS when available."""
    if not q:
        return queryset

    if _pg_search_active():
        vector = (
            SearchVector('name',             weight='A') +
            SearchVector('cas_number',       weight='B') +
            SearchVector('e_number',         weight='B') +
            SearchVector('alternative_names', weight='B') +
            SearchVector('description',      weight='C') +
            SearchVector('specifications',   weight='D')
        )
        search_query = SearchQuery(q)
        return (
            queryset
            .annotate(rank=SearchRank(vector, search_query))
            .filter(
                Q(rank__gt=0) |
                Q(cas_number__icontains=q) |
                Q(e_number__icontains=q)
            )
            .order_by('-rank', 'name')
        )

    # SQLite / non-Postgres fallback
    return queryset.filter(
        Q(name__icontains=q) |
        Q(cas_number__icontains=q) |
        Q(e_number__icontains=q) |
        Q(alternative_names__icontains=q) |
        Q(description__icontains=q) |
        Q(specifications__icontains=q)
    )


def _apply_filters(queryset, request):
    """Apply sidebar filters (certification, application, origin) from GET params."""
    cert_slugs = request.GET.getlist('cert')
    app_slugs  = request.GET.getlist('app')
    origin     = request.GET.get('origin', '').strip()

    if cert_slugs:
        queryset = queryset.filter(certifications__slug__in=cert_slugs).distinct()
    if app_slugs:
        queryset = queryset.filter(applications__slug__in=app_slugs).distinct()
    if origin:
        queryset = queryset.filter(origin=origin)

    return queryset


def _filter_context(request):
    """Build context data needed to render the filter sidebar."""
    return {
        'all_certifications': Certification.objects.all(),
        'all_applications': Application.objects.all(),
        'origin_choices': ORIGIN_CHOICES,
        'active_certs': request.GET.getlist('cert'),
        'active_apps': request.GET.getlist('app'),
        'active_origin': request.GET.get('origin', ''),
    }


def _paginate(request, queryset):
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page', 1))


# Views

def product_list_all(request):
    all_categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category').order_by('name')

    q = request.GET.get('q', '').strip()
    products = _apply_filters(products, request)
    products = _search_products(products, q)

    page = _paginate(request, products)

    context = {
        'category': None,
        'all_categories': all_categories,
        'page': page,
        'q': q,
        **_filter_context(request),
    }

    if request.headers.get('X-GFI-Partial') == 'cards':
        return render(request, 'products/_product_cards.html', context)

    if request.headers.get('X-GFI-Partial'):
        return render(request, 'products/_products_grid.html', context)

    return render(request, 'products/list.html', context)


def product_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    all_categories = Category.objects.all()
    products = (
        Product.objects
        .filter(category=category, is_active=True)
        .select_related('category')
        .order_by('name')
    )

    q = request.GET.get('q', '').strip()
    products = _apply_filters(products, request)
    products = _search_products(products, q)

    page = _paginate(request, products)

    context = {
        'category': category,
        'all_categories': all_categories,
        'page': page,
        'q': q,
        **_filter_context(request),
    }

    if request.headers.get('X-GFI-Partial') == 'cards':
        return render(request, 'products/_product_cards.html', context)

    if request.headers.get('X-GFI-Partial'):
        return render(request, 'products/_products_grid.html', context)

    return render(request, 'products/category.html', context)


def product_search(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if q:
        products = _search_products(
            Product.objects.filter(is_active=True).select_related('category'),
            q
        )
    return render(request, 'products/search.html', {'products': products, 'q': q})


def search_suggest(request):
    """Return up to 5 categories + 5 products matching `q` as JSON."""
    from django.urls import reverse
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'categories': [], 'products': []})

    categories = (
        Category.objects
        .filter(name__icontains=q)
        .order_by('order', 'name')[:5]
    )
    products_qs = Product.objects.filter(is_active=True).select_related('category')
    products_qs = _search_products(products_qs, q)[:5]

    return JsonResponse({
        'categories': [
            {
                'name': c.name,
                'url':  reverse('products:category', args=[c.slug]),
            }
            for c in categories
        ],
        'products': [
            {
                'name': p.name,
                'category': p.category.name,
                'url': reverse('products:detail', args=[p.category.slug, p.slug]),
            }
            for p in products_qs
        ],
    })


def product_detail(request, category_slug, slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = get_object_or_404(
        Product.objects.prefetch_related('certifications', 'applications'),
        slug=slug, category=category, is_active=True
    )
    related = (
        Product.objects
        .filter(category=category, is_active=True)
        .exclude(pk=product.pk)
        .order_by('name')[:4]
    )
    return render(request, 'products/detail.html', {
        'product':  product,
        'category': category,
        'related':  related,
    })
