from django.urls import path

from . import views

app_name = 'products'

urlpatterns = [
    path('', views.category_list, name='list'),
    path('search/', views.product_search, name='search'),
    path('<slug:category_slug>/', views.product_list, name='category'),
    path('<slug:category_slug>/<slug:slug>/', views.product_detail, name='detail'),
]
