from django.shortcuts import render

from apps.products.models import Category


def home(request):
    categories = Category.objects.all()
    return render(request, 'pages/home.html', {'categories': categories})


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')
