from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from expenses import views
from expenses import models


class TestUrls(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = get_user_model().objects.create_user(
            username='test user one',
            email='user1@user.com',
            password='user1password',
        )
        cls.user_2 = get_user_model().objects.create_user(
            username='test user tow',
            email='user2@user.com',
            password='user2password',
        )
        cls.group = models.Grupe.objects.create(
            name='test group'
        )
        cls.group.members.set([cls.user_1, cls.user_2])
        cls.expense = models.Expense.objects.create(
            grupe=cls.group,
            description='test expense',
            amount=10,
            created_by=cls.user_1,
        )
        cls.expense.participants.set([cls.user_1, cls.user_2])
        cls.client = Client()
        user_1_login = cls.client.login(username='test user one', password='user1password')
        user_2_login = cls.client.login(username='test user tow', password='user2password')
        assert user_1_login and user_2_login, 'the user should be logged in'

    def test_group_list_url(self):
        url = reverse('expenses:group-list')
        self.assertEqual(resolve(url).func, views.group_list_view)

    def test_profile_url(self):
        url = reverse('expenses:profile')
        self.assertEqual(resolve(url).func, views.profile_view)

    def test_group_detail_url(self):
        url = reverse('expenses:group-detail', kwargs={'pk': self.group.pk})
        self.assertEqual(resolve(url).func, views.group_detail_view)

    def test_group_update_url(self):
        url = reverse('expenses:group-edit', kwargs={'pk': self.group.pk})
        self.assertEqual(resolve(url).func.view_class, views.GrupeUpdateView)

    def test_create_new_expense_url(self):
        url = reverse('expenses:group-expense-new', kwargs={'pk': self.group.pk})
        self.assertEqual(resolve(url).func, views.create_expense_view)

    def test_transaction_create_url(self):
        url = reverse('expenses:transaction-new', kwargs={'pk': self.expense.pk})
        self.assertEqual(resolve(url).func, views.create_transactions_view)
