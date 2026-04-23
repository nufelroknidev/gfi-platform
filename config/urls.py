from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from apps.pages.sitemaps import NewsSitemap, ProductSitemap, StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'news': NewsSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon-48.png', permanent=True)),
]

urlpatterns += [
    path('summernote/', include('django_summernote.urls')),
]

urlpatterns += [
    path('admin/', admin.site.urls),
    path('', include('apps.pages.urls')),
    path('products/', include('apps.products.urls')),
    path('news/', include('apps.news.urls')),
    path('contact/', include('apps.contact.urls')),
]

if settings.DEBUG:
    from django.shortcuts import render as _render
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__test-404__/', lambda r: _render(r, '404.html'), name='test_404')]
    urlpatterns += [path('__test-500__/', lambda r: _render(r, '500.html'), name='test_500')]
