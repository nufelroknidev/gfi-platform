import json
import re

from django.db import connection
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from .models import Application, Category, Certification, Product, ORIGIN_CHOICES

PRODUCTS_PER_PAGE = 12

try:
    from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
    _PG_SEARCH_AVAILABLE = True
except ImportError:
    _PG_SEARCH_AVAILABLE = False


def _pg_search_active():
    return _PG_SEARCH_AVAILABLE and connection.vendor == 'postgresql'


def _normalize_query(q):
    """
    Normalize a raw search string for B2B food-additive lookups.
    Returns (normalized_q, cas_digits, enumber_norm).
      cas_digits   — query with hyphens stripped, for CAS lookup without punctuation
      enumber_norm — uppercase E-number (e.g. 'E407'), or None
    """
    q = ' '.join(q.split())  # collapse whitespace

    # CAS: strip hyphens so "50817" and "50-81-7" both match
    cas_digits = re.sub(r'[-\s]', '', q)

    # E-number: match e/E followed by digits (with optional space/hyphen)
    enumber_norm = None
    m = re.fullmatch(r'[eE]\s*(\d+[a-zA-Z]*)', q.replace('-', '').replace(' ', ''))
    if m:
        enumber_norm = 'E' + m.group(1).upper()

    return q, cas_digits, enumber_norm


def _search_products(queryset, q):
    """Apply keyword search, using PostgreSQL FTS when available."""
    if not q:
        return queryset

    q, cas_digits, enumber_norm = _normalize_query(q)

    if _pg_search_active():
        search_query = SearchQuery(q, search_type='websearch')
        # Use the stored search_vector when it has been populated; otherwise
        # fall back to computing a vector on the fly (e.g. newly inserted rows).
        qs = (
            queryset
            .annotate(rank=SearchRank('search_vector', search_query))
            .filter(
                Q(rank__gt=0) |
                Q(name__icontains=q) |
                Q(cas_number__icontains=q) |
                Q(cas_number__icontains=cas_digits) |
                Q(e_number__icontains=enumber_norm or q) |
                Q(alternative_names__icontains=q)
            )
            .order_by('-rank', 'name')
        )
        return qs

    # SQLite / non-Postgres fallback
    f = (
        Q(name__icontains=q) |
        Q(cas_number__icontains=q) |
        Q(alternative_names__icontains=q) |
        Q(description__icontains=q) |
        Q(specifications__icontains=q) |
        Q(available_forms__icontains=q)
    )
    if cas_digits != q:
        f |= Q(cas_number__icontains=cas_digits)
    if enumber_norm:
        f |= Q(e_number__icontains=enumber_norm)
    else:
        f |= Q(e_number__icontains=q)
    return queryset.filter(f)


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
        'all_applications':   Application.objects.all(),
        'origin_choices':     ORIGIN_CHOICES,
        'active_certs':       request.GET.getlist('cert'),
        'active_apps':        request.GET.getlist('app'),
        'active_origin':      request.GET.get('origin', ''),
    }


def _paginate(request, queryset):
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page', 1))


# ── Views ─────────────────────────────────────────────────────────────────────

def product_list_all(request):
    all_categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category').order_by('name')

    q = request.GET.get('q', '').strip()
    products = _apply_filters(products, request)
    products = _search_products(products, q)

    page = _paginate(request, products)

    context = {
        'category':       None,
        'all_categories': all_categories,
        'page':           page,
        'q':              q,
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
        'category':       category,
        'all_categories': all_categories,
        'page':           page,
        'q':              q,
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
    page = _paginate(request, products)
    return render(request, 'products/search.html', {'page': page, 'products': page.object_list, 'q': q})


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
                'name':     p.name,
                'category': p.category.name,
                'url':      reverse('products:detail', args=[p.category.slug, p.slug]),
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
        .select_related('category')
        .order_by('name')[:4]
    )
    return render(request, 'products/detail.html', {
        'product':  product,
        'category': category,
        'related':  related,
    })
