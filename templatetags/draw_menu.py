from django import template

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.safestring import mark_safe

from menu.models import Menu
from menu.models import Branch


register = template.Library()

""" New Correct caching """
def compile_branch_cached(branch, compiled_menu_cached, queryset_cached):
    branches = []
    for _branch in queryset_cached:
        if _branch['parent_id'] == branch['id']:
            branches.append(_branch)

    if len(branches) != 0:
        for _branch in branches:
            compiled_menu_cached.append(_branch)
            compiled_menu_cached = compile_branch_cached(_branch, compiled_menu_cached, queryset_cached)
        # branches = queryset.filter(parent=_branch)
    return compiled_menu_cached

""" Old Incorrect caching """
# def compile_branch(branch, compiled_menu, queryset):
#     branches = queryset.filter(parent=branch)
#     if branches.count() != 0:
#         for _branch in branches:
#             compiled_menu.append(_branch)
#             compiled_menu = compile_branch(_branch, compiled_menu, queryset)
#         branches = queryset.filter(parent=_branch)
#     return compiled_menu

def get_parent(queryset_cached, parent_id):
    parent = None
    for _branch in queryset_cached:
        if _branch['id'] == parent_id:
            parent = _branch
            break
    return parent

def make_menu_data(path, name):
    """ Compile data to render menu """

    """ New Correct caching """
    if not cache.get(name) is None:
        queryset_cached = cache.get(name)
    else:
        cache.set(name, list(Branch.objects.filter(menu__name=name).values()))
        queryset_cached = cache.get(name)

    compiled_menu_cached = []
    for branch in queryset_cached:
        if branch['parent_id'] is None:
            compiled_menu_cached.append(branch)
            compiled_menu_cached = compile_branch_cached(
                branch,
                compiled_menu_cached,
                queryset_cached)

    current_branch = None
    for _branch in queryset_cached:
        if _branch['slug_cached'] == path:
            current_branch = _branch

    if current_branch:
        current_slug = current_branch['slug_cached']
        parent_id = current_branch['parent_id']
        parent = get_parent(queryset_cached, parent_id)
        open_branches = [current_branch, ]
        for child in queryset_cached:
            if child['parent_id'] == current_branch['id']:
                open_branches.append(child)
    else:
        current_slug = None
        parent = None
        current_branch = None
        open_branches = []

    if not current_slug is None:
        while not parent_id is None:
            parent = get_parent(queryset_cached, parent_id)
            parent_id = parent['parent_id']
            open_branches.append(parent)

    """ Old Incorrect caching """
    # compiled_menu = []
    # if not cache.get(name) is None:
    #     print('Taking form cache', )
    #     queryset = cache.get(name)
    # else:
    #     print('Seting new cache', name)
    #     queryset = Branch.objects.filter(menu__name=name)
    #     cache.set(name, queryset)
    #
    #
    # for branch_level in cache.get(name).filter(menu__name=name, parent=None):
    #     compiled_menu.append(branch_level)
    #     # compiled_menu = compile_branch(branch_level, compiled_menu, queryset)
    #     compiled_menu = compile_branch(branch_level, compiled_menu, cache.get(name))
    #
    # try:
    #     current_branch = cache.get(name).get(slug_cached=path)
    # except ObjectDoesNotExist:
    #     current_slug = None
    #     parent = None
    #     current_branch = None
    #     open_branches = []
    # else:
    #     current_slug = current_branch.slug_cached
    #     parent = current_branch.parent
    #     open_branches = [current_branch, ]
    #     for child in cache.get(name).filter(parent=current_branch):
    #         open_branches.append(child)
    #
    # if not current_slug is None:
    #     while not parent is None:
    #         open_branches.append(parent)
    #         parent = parent.parent

    # print(open_branches)
    # print(compiled_menu, current_branch, current_slug, open_branches)
    # return compiled_menu, current_branch, current_slug, open_branches
    return compiled_menu_cached, current_branch, current_slug, open_branches

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