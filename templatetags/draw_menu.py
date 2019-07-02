from django import template

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.safestring import mark_safe

from menu.models import Menu
from menu.models import Branch


register = template.Library()

def compile_branch(branch, compiled_menu, queryset):
    branches = queryset.filter(parent=branch)
    if branches.count() != 0:
        for _branch in branches:
            compiled_menu.append(_branch)
            compiled_menu = compile_branch(_branch, compiled_menu, queryset)
        branches = queryset.filter(parent=_branch)
    return compiled_menu

def make_menu_data(path, name):
    """ Compile data to render menu """
    try:
        menu = Menu.objects.get(name=name)
    except ObjectDoesNotExist:
        return None, None, None, None
    else:
        compiled_menu = []
        if not cache.get(name) is None:
            print('Taking form cache', )
            queryset = cache.get(name)
        else:
            print('Seting new cache', name)
            queryset = Branch.objects.filter(menu=menu)
            cache.set(name, queryset)

        for branch_level in queryset.filter(menu=menu, parent=None):
            compiled_menu.append(branch_level)
            compiled_menu = compile_branch(branch_level, compiled_menu, queryset)

        try:
            current_branch = queryset.get(slug_cached=path)
        except ObjectDoesNotExist:
            current_slug = None
            parent = None
            current_branch = None
            open_branches = []
        else:
            current_slug = current_branch.slug_cached
            parent = current_branch.parent
            open_branches = [current_branch, ]
            for child in queryset.filter(parent=current_branch):
                open_branches.append(child)

        if not current_slug is None:
            while not parent is None:
                open_branches.append(parent)
                parent = parent.parent

        # print(open_branches)
        return compiled_menu, current_branch, current_slug, open_branches

@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, name):
    path = context['request'].path
    
    compiled_menu, current_branch, current_slug, open_branches = make_menu_data(path, name)

    return {
        'branches':compiled_menu,
        'current_branch': current_branch,
        'current_slug': current_slug,
        'open_branches': open_branches,
        }