# -*- coding: utf-8 -*-

from django import forms
from th_readability.models import Readability


class ReadabilityForm(forms.ModelForm):

    """
        for to handle Readability service
    """

    class Meta:
        model = Readability
        fields = ('tag',)


class ReadabilityProviderForm(ReadabilityForm):
    pass


class ReadabilityConsummerForm(ReadabilityForm):
    pass
