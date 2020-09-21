from django.shortcuts import render
from .models import init_db

def init(request):
    init_db()
    return render(request, 'index.html')
