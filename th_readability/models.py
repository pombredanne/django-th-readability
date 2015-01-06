# -*- coding: utf-8 -*-

from django.db import models
from django_th.models.services import Services


class Readability(Services):

    # put whatever you need  here

    # but keep at least this one
    tag = models.CharField(max_length=80, blank=True)
    trigger = models.ForeignKey('TriggerService')

    class Meta:
        app_label = 'django_th'
        db_table = 'django_th_readability'

    def __unicode__(self):
        return "%s" % (self.name)

    def show(self):
        return "My Readability %s" % (self.name)
