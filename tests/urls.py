from django.urls import path, include
from django.conf.urls import include, url

# from .views import *
def foo(request):
    return None

urlpatterns = [
    path(r'foo/bar/baz/quux/', foo, name='foo_bar_baz_quux'),
]