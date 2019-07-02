from django.urls import path, include
from django.conf.urls import include, url

from .views import *

app_name = 'menu'

def foo():
    return None

urlpatterns = [
    path(r'', index, name='index'),
]