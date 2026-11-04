from django.shortcuts import render, redirect

# Create your views here.

def welcome(request):
    if request.user.is_authenticated:
        return redirect('core:index')
    return render(request, 'core/welcome.html')

def index(request):
    return render(request, "core/index.html")

def about(request):
    return render(request, "core/about.html")

