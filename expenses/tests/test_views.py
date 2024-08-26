from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

from expenses import models


class TestViews(TestCase):
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
        cls.user_3 = get_user_model().objects.create_user(
            username='test user three',
            email='user3@user.com',
            password='user3password',
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

    def test_group_list_view_get(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'

        response = self.client.get(reverse('expenses:group-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_list_view.html')

    def test_group_list_view_post(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.post(reverse('expenses:group-list'), {
            'name': 'test group',
            'members': [self.user_1, self.user_2]
        })
        self.assertEqual(response.status_code, 200)

    def test_group_detail_view_get(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.get(reverse('expenses:group-detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)

    def test_group_detail_view_members_in_context(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.get(reverse('expenses:group-detail', args=[self.group.id]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('group_members', response.context)
        self.assertEqual(len(response.context['group_members']), 2)

    def test_group_detail_view_context(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'

        response = self.client.get(reverse('expenses:group-detail', args=[self.group.id]))
        self.assertIn('group_members', response.context)
        self.assertIn('expenses', response.context)
        self.assertIn('group', response.context)
        self.assertIn('member_form', response.context)

    def test_group_detail_view_user_not_allowed_see_detail(self):
        login = self.client.login(username='test user three', password='user3password')
        assert login, 'you should be logged in'

        response = self.client.get(reverse('expenses:group-detail', args=[self.group.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('expenses:group-list'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You are not allowed to view this group')

    def test_create_expense_view_get(self):
        login = self.client.login(username='test user three', password='user3password')
        assert login, 'you should be logged in'

        response = self.client.get(reverse('expenses:group-expense-new', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expense_create_view.html')

    def test_create_expense_view_initial_data_in_form(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.get(reverse('expenses:group-expense-new', args=[self.group.id]))
        form = response.context['form']
        self.assertEqual(form.initial['grupe'], self.group)
        self.assertEqual(form.initial['created_by'], self.user_1)

    def test_create_expense_view_post(self):
        login = self.client.login(username='test user three', password='user3password')
        assert login, 'you should be logged in'
        self.client.get(reverse('expenses:group-expense-new', args=[self.group.id]))
        response = self.client.post(reverse('expenses:group-expense-new', args=[self.group.id]), data={
            'description': 'test expense 2',
            'amount': 20,
            'participants': [self.user_1.id, self.user_2.id],
            'grupe': self.group.id,
            'created_by': self.user_1.id,
        })
        if response.status_code != 302:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Expense.objects.count(), 2)

    def test_transaction_view_get_redirect_user_if_not_logged_in(self):
        response = self.client.get(reverse('expenses:transaction-new', args=[self.expense.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/expenses/{self.expense.id}/transaction/new/')

    def test_transaction_view_get_allow_user_if_logged_in(self):
        login = self.client.login(username='test user three', password='user3password')
        assert login, 'you should be logged in'
        response = self.client.get(reverse('expenses:transaction-new', args=[self.expense.id]))
        self.assertEqual(response.status_code, 200)

    def test_transaction_create_view_get_initial_data_in_form(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.get(reverse('expenses:transaction-new', args=[self.expense.id]))
        form = response.context['form']
        self.assertEqual(form.initial['from_user'], self.user_1)
        self.assertEqual(form.initial['to_user'], self.expense.created_by)
        self.assertEqual(form.initial['amount'], round(self.expense.amount / self.expense.participants.count(), 2))

    def test_transaction_create_view_post_if_user_amount_is_enough(self):
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        response = self.client.post(reverse('expenses:transaction-new', args=[self.expense.id]), data={
            'expense': self.expense.id,
            'from_user': self.user_1.id,
            'to_user': self.expense.created_by_id,
            'amount': round(self.expense.amount / self.expense.participants.count(), 2)
        })
        if response.status_code != 302:
            print(response.context['form'].errors)
        self.assertRedirects(response, f'/expenses/detail/{self.expense.grupe.id}/')
        self.assertEqual(models.Transaction.objects\
                         .filter(from_user=self.user_1, expense=self.expense.id)\
                         .exists(), True)

    def test_transaction_create_view_post_if_user_amount_is_not_enough(self):
        expense_2 = models.Expense.objects.create(
            grupe=self.group,
            description='test expense',
            amount=10,
            created_by=self.user_2,
        )
        expense_2.participants.set([self.user_1, self.user_2])
        login = self.client.login(username='test user one', password='user1password')
        assert login, 'you should be logged in'
        self.user_1.account.balance = 0
        self.user_1.account.save()
        response = self.client.post(reverse('expenses:transaction-new', args=[expense_2.id]), data={
            'expense': expense_2.id,
            'from_user': self.user_1.id,
            'to_user': expense_2.created_by_id,
            'amount': round(expense_2.amount / expense_2.participants.count(), 2)
        })
        self.assertContains(response, f'Insufficient balance: Your account balance is {self.user_1.account.balance:.2f}.')



