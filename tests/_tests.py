# encoding=utf-8

from django.test import TestCase
import django.core.validators as validators

from menu.models import Menu
from menu.models import Branch

from menu.templatetags.draw_menu import make_menu_data

MENUS = [
    {'title': 'Menu1','name': 'menu1',},
    {'title': 'Menu2','name': 'menu2',},
    {'title': 'My Little Pony','name': 'mlp',},
    {'title': 'Incorrect name','name': 'incorrect_name+~//и вообще…',}
]

BRANCHES = [
    {'menu':'mlp', 'parent':None, 'title':'Equestria', 'slug':'equestria',},
    {'menu':'menu1', 'parent':None, 'title':'Crystal Germs', 'slug':'germs',},
    {'menu':'mlp', 'parent':'/equestria/', 'title':'Fluttershy', 'slug':'fluttershy',},
    {'menu':'mlp', 'parent':'/equestria/fluttershy/', 'title':'Fans', 'slug':'fans',},
    {'menu':'mlp', 'parent':'/equestria/fluttershy/fans/', 'title':'Brony_1', 'slug':'brony1',},
    {'menu':'mlp', 'parent':'/equestria/fluttershy/fans/', 'title':'Brony_2', 'slug':'brony2',},
    {'menu':'mlp', 'parent':'/equestria/fluttershy/fans/brony1/', 'title':'Shed', 'slug':'shed',},
]

def foo(request):
    return None

class CommonTests(TestCase):
    def setUp(self):
        for menu in MENUS:
            try:
                Menu.objects.create(title=menu['title'], name=menu['name'])
            except:
                pass
        
        for branch in BRANCHES:
            if not branch['parent'] is None:
                parent = Branch.objects.get(slug_cached=branch['parent'])
            else:
                parent = None
            Branch.objects.create(
                menu=Menu.objects.get(name=branch['menu']),
                parent=parent,
                title=branch['title'],
                slug=branch['slug']
            )


    def test_menus_creation(self):
        self.assertEqual(Menu.objects.all().count(), 4)
        with self.assertRaises(validators.ValidationError):
            Menu.objects.get(title='Incorrect name').full_clean()


    def test_branch_creation(self):
        self.assertEqual(Branch.objects.all().count(), len(BRANCHES))


    def test_branch_cascade_cache_update(self):
        equestria = Branch.objects.get(slug_cached="/equestria/")
        shed = Branch.objects.get(title='Shed', slug='shed')
        self.assertTupleEqual(
            (shed.slug_cached, shed.title_cached, shed.url_cached),
            (
                '/equestria/fluttershy/fans/brony1/shed/',
                'Equestria / Fluttershy / Fans / Brony_1 / Shed',
                '/equestria/fluttershy/fans/brony1/shed/'),
            )

        equestria.title = 'Eques3a'
        equestria.slug = 'eques3a'
        equestria.save()

        shed = Branch.objects.get(title='Shed', slug='shed')
        self.assertTupleEqual(
            (shed.slug_cached, shed.title_cached, shed.url_cached),
            (
                '/eques3a/fluttershy/fans/brony1/shed/',
                'Eques3a / Fluttershy / Fans / Brony_1 / Shed',
                '/eques3a/fluttershy/fans/brony1/shed/'),
            )


    def test_template_tag(self):
        """ Incorrect menu """
        compiled_menu, current_branch, current_slug, open_branches = make_menu_data('/foo/bar/', 'foo')
        self.assertTupleEqual(
            (compiled_menu, current_branch, current_slug, open_branches),
            (None, None, None, None)
            )
        
        """ Correct menu on not matchin url """
        compiled_menu, current_branch, current_slug, open_branches = make_menu_data('/foo/bar/', 'mlp')
        self.assertTupleEqual(
            (current_branch, current_slug, open_branches),
            (None, None, [])
            )
        
        """ Correct menu on matching url """
        compiled_menu, current_branch, current_slug, open_branches = make_menu_data(
            '/equestria/fluttershy/fans/',
            'mlp')
        self.assertListEqual(
            [
                Branch.objects.get(slug_cached="/equestria/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/brony1/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/brony1/shed/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/brony2/"),
            ],
            compiled_menu
        )
        self.assertEqual(
            Branch.objects.get(slug_cached="/equestria/fluttershy/fans/"),
            current_branch
        )
        self.assertEqual(
            "/equestria/fluttershy/fans/",
            current_slug
        )
        self.assertListEqual(
            [
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/brony1/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/fans/brony2/"),
                Branch.objects.get(slug_cached="/equestria/fluttershy/"),
                Branch.objects.get(slug_cached="/equestria/"),
            ],
            open_branches
        )

    def test_url_logic(self):
        equestria = Branch.objects.get(title="Equestria")
        
        """ URL """
        equestria.url = "https://foo.bar/baz/"
        equestria.save()
        self.assertEqual(equestria.url_cached, "https://foo.bar/baz/")
        
        """ URL and incorrect named url """
        equestria.url = "https://foo.bar/baz/"
        equestria.named_url = "foo-bar"
        equestria.save()
        self.assertEqual(equestria.url_cached, "https://foo.bar/baz/")

        """ URL and incorrect named url """
        from django.urls import reverse
        from django.urls import path
        urlpatterns = [
            path(r'/foo/bar/baz/quux/', foo, name='foo_bar_baz_quux'),
        ]
        print(reverse('foo_bar_baz_quux', urlconf=[path(r'/foo/bar/baz/quux/', foo, name='foo_bar_baz_quux'),]))
        # equestria.url = "https://foo.bar/baz/"
        # equestria.named_url = "index"
        # equestria.save()
        # self.assertEqual(equestria.url_cached, "")