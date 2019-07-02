# encoding=utf-8

from django.core.exceptions import ValidationError
from django.core.cache import cache

from django.urls import reverse

from django.db import models
from django.db.models.signals import pre_save
from django.db.models.signals import post_save

from django.dispatch import receiver
from .menu import Menu

def refresh_all_menu_branches(menu):
    for child in Branch.objects.filter(
        menu=menu,
        parent=None, # No need to get all they will do it themselves
    ):
        child.refresh_cache()

def refresh_cache(instance):
    """ Generate current cache values for Branch instance """
    
    parent = instance
    _title_cached = [str(instance.title)]
    _slug_cached = []
    while parent:
        _title_cached.append(parent.title)
        _slug_cached.append(parent.slug)
        parent = parent.parent
    
    _title_cached.reverse()
    _slug_cached.reverse()
    
    title_cached = _title_cached[0]
    slug_cached = "/"
    for branch in _title_cached[1:-1]:
        title_cached = "%s / %s" % (title_cached, branch)
    for slug in _slug_cached:
        slug_cached = "%s%s/" % (slug_cached, slug)
    
    if instance.url is None and instance.url_named is None:
        url_cached = slug_cached
    elif instance.url_named is None:
        url_cached = instance.url
    else:
        url_cached = instance.url_named
        try:
            url_cached = reverse(instance.url_named)
        except:
            if instance.url:
                url_cached = instance.url
            else:
                url_cached = slug_cached
    
    if instance.parent != None:
        level_cached = instance.parent.level_cached + 1
    else:
        level_cached = 0
        
    return title_cached, slug_cached, url_cached, level_cached


class Branch(models.Model):
    """
    Menu branch model
    
    If parent filed is None, it means that this branch is root for its menu
    """
    
    menu = models.ForeignKey('Menu',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        )

    """ Branch.parent field can not be the 'self' value """
    parent = models.ForeignKey('self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        )

    title = models.CharField(
        verbose_name='Title',
        max_length=128,
        blank=False,
        )
    
    title_cached = models.CharField(
        verbose_name='Title cached',
        max_length=128,
        blank=True,
        null=True,
        )
    
    slug = models.SlugField(
        verbose_name='URL slug',
        allow_unicode=True,
        )

    slug_cached = models.SlugField(
        verbose_name='URL cached slug',
        allow_unicode=True,
        blank=True,
        null=True,
        )
    
    url_named = models.CharField(
        verbose_name='Named url',
        max_length=2048,
        blank=True,
        null=True,
        )
    
    url = models.URLField(
        verbose_name='Pure url',
        max_length=2048,
        blank=True,
        null=True,
        )
        
    url_cached = models.CharField(
        verbose_name='Url cahed',
        max_length=2048,
        blank=True,
        null=True,
        )

    level_cached = models.PositiveSmallIntegerField(
        verbose_name='Branch level',
        blank=False,
        null=False,
        default=0,
        )

    def __str__(self):
        return "{menu} | {title_cached}".format(menu=self.menu, title_cached=self.title_cached)

    @property
    def childs(self):
        return Branch.objects.filter(parent=self)

    def refresh_cache(self):
        title_cached, slug_cached, url_cached, level_cached = refresh_cache(self)

        if self.slug_cached != slug_cached or self.title_cached != title_cached or self.url_cached != url_cached:
            if self.slug_cached != slug_cached:
                self.slug_cached = slug_cached
            if self.title_cached != title_cached:
                self.title_cached = title_cached
            if self.url_cached != url_cached:
                self.url_cached = url_cached
            self.save()
            print('Clean Cache', self.menu.name)
            cache.delete(self.menu.name)


@receiver(post_save, sender=Branch)
def set_child_branches_cached_values(sender, instance, **kwargs):
    """ Refresh all childs"""
    for child in instance.childs:
        child.refresh_cache()

@receiver(pre_save, sender=Branch)
def set_branch_cached_values(sender, instance, **kwargs):
    if instance.parent != None:
        instance.level_cached = instance.parent.level_cached + 1

    title_cached, slug_cached, url_cached, level_cached = refresh_cache(instance)
    if instance.slug_cached != slug_cached or instance.title_cached != title_cached or instance.url_cached != url_cached or instance.level_cached != level_cached:
        if instance.slug_cached != slug_cached:
            instance.slug_cached = slug_cached
        if instance.title_cached != title_cached:
            instance.title_cached = title_cached
        if instance.url_cached != url_cached:
            instance.url_cached = url_cached
        if instance.level_cached != level_cached:
            instance.level_cached = level_cached
        print('Clean Cache', instance.menu.name)
        cache.delete(instance.menu.name)

    if instance.parent == instance:
        raise ValidationError('You can not set "self" instance as a Branch.parent')