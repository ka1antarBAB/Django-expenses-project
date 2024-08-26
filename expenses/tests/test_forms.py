from django.test import TestCase
from django.contrib.auth import get_user_model

from expenses import forms
from expenses import models


class TestForms(TestCase):
    def setUp(self):
        self.user_1 = get_user_model().objects.create_user(
            username='test user one',
            email='user1@user.com',
            password='user1password',
        )
        self.user_2 = get_user_model().objects.create_user(
            username='test user tow',
            email='user2@user.com',
            password='user2password',
        )
        self.group = models.Grupe.objects.create(
            name='test group'
        )
        self.group.members.set([self.user_1, self.user_2])
        self.expense = models.Expense.objects.create(
            grupe=self.group,
            description='test expense',
            amount=10,
            created_by=self.user_1,
        )
        self.expense.participants.set([self.user_1, self.user_2])

    def test_grupe_form(self):
        form = forms.GrupeForm(data={
            'name': 'test group',
            'members': [self.user_1.id, self.user_2.id],
        })
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_transaction_form(self):
        form = forms.TransactionForm(data={
            'from_user': self.user_1.id,
            'to_user': self.user_2.id,
            'amount': 10,
            'expense': self.expense.id,
        })
        self.assertTrue(form.is_valid())
