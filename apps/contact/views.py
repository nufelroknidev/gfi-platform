from django.shortcuts import render


def inquiry(request):
    return render(request, 'contact/inquiry.html')
