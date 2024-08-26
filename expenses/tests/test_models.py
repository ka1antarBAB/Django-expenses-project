from django.test import TestCase
from django.contrib.auth import get_user_model
from expenses import models


class TestModels(TestCase):
    def test_user_creation_signal(self):
        user = get_user_model().objects.create_user(
            username='testusersignal',
            email='testuser@testuser.come',
            password='testuserpassword'
        )
        self.assertTrue(models.Account.objects.filter(user=user).exists())
        account = models.Account.objects.get(user=user)
        self.assertEqual(account.balance, 100)
