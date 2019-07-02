from django.contrib import admin

from .models import Menu
from .models import Branch

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    pass

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    readonly_fields = ['title_cached', 'slug_cached', 'level_cached', 'url_cached']
    list_filter = ('menu',)
    pass