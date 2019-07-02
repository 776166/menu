from django.shortcuts import render

# Create your views here.
from menu.models import Menu

def index(request):
    context = {
        'menues': Menu.objects.all()
    }
    return render(request, 'menu/admin/index.html', context)