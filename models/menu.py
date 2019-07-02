# encoding=utf-8

from django.core.validators import RegexValidator

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver

from menu.helpers import compile_menu

class Menu(models.Model):
    """
    Menu instance model
    """

    title = models.CharField(
        verbose_name='Menu title',
        max_length=128,
        blank=False,
    )
    
    name = models.CharField(
        verbose_name='Menu system name (^[-a-zA-Z0-9_]+$)',
        max_length=32,
        validators=[
            RegexValidator(regex='^[-a-zA-Z0-9_]+$'),
            ]
        )
    
    def __str__(self):
        return self.title
    #
    # @property
    # def compiled_menu(self):
    #     return compile_menu(self.id)

@receiver(post_save, sender=Menu)
def set_child_branches_cached_values(sender, instance, **kwargs):
    """ Refresh all childs"""
    from .branch import refresh_all_menu_branches
    
    refresh_all_menu_branches(instance)