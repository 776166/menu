# encoding=utf-8


def compile_menu(menu_id):
    from .models.branch import Branch
    branches = Branch.objects.filter(menu=menu_id).values(
        'id',
        'parent_id',
        'title',
        'slug',
        )
    print('compile_menu', list(branches))
    
    # for root_branch in branches.filter
    return list(branches)
    # return ['foo', 'bar', ['foo', 'bar'], {'foo':'foo', 'bar':{'bar':'baz'}}]