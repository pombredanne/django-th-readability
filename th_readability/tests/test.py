# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from th_readability.models import Readability
from django_th.models import TriggerService, UserService, ServicesActivated
from th_readability.forms import ReadabilityProviderForm, ReadabilityConsumerForm


class readabilityTest(TestCase):

    """
        ReadabilityTest Model
    """
    def setUp(self):
        try:
            self.user = User.objects.get(username='john')
        except User.DoesNotExist:
            self.user = User.objects.create_user(
                username='john', email='john@doe.info', password='doe')

    def create_triggerservice(self, date_created="20130610",
                              description="My first Service", status=True):
        user = self.user
        service_provider = ServicesActivated.objects.create(
            name='ServiceRss', status=True,
            auth_required=False, description='Service RSS')
        service_consumer = ServicesActivated.objects.create(
            name='ServiceReadability', status=True,
            auth_required=True, description='Service Readability')
        provider = UserService.objects.create(user=user,
                                              token="",
                                              name=service_provider)
        consumer = UserService.objects.create(user=user,
                                              token="AZERTY1234",
                                              name=service_consumer)
        return TriggerService.objects.create(provider=provider,
                                             consumer=consumer,
                                             user=user,
                                             date_created=date_created,
                                             description=description,
                                             status=status)

    def create_readability(self):
        trigger = self.create_triggerservice()
        name = 'test'
        tag = 'test tag'
        status = True
        return Readability.objects.create(name=name,
                                          tag=tag,
                                          trigger=trigger,
                                          status=status)

    def test_readability(self):
        r = self.create_readability()
        self.assertTrue(isinstance(r, Readability))
        self.assertEqual(r.show(), "My Readability %s" % (r.name))

    """
        Form
    """
    # no need to test if the tag is filled or not as it's not mandatory
