from django.contrib import admin, messages
from django.db.models import Count
from django.shortcuts import reverse
from django.utils.html import urlencode, format_html
from django.db.models import Prefetch

from expenses.models import Expense, Transaction, Group, Account


# Register your models here.


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'datetime_created', 'num_of_transaction')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related(Prefetch(
                'transactions',
                queryset=Transaction.objects.select_related('expense'),
            ))
            .annotate(num_of_transaction=Count('transactions'))
        )

    @admin.display(description='# transactions', ordering='num_of_transaction')
    def num_of_transaction(self, obj):
        url = (
                reverse('admin:expenses_transaction_changelist')
                + '?'
                + urlencode({'expense__id': obj.id})
        )
        return format_html('<a href="{}">{}</a>', url, obj.num_of_transaction)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'amount', 'to_user', 'datetime_created',)
    select_related = ('from_user', 'to_user')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_of_expenses')

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('expenses') \
            .annotate(
            num_of_expenses=Count('expenses')
        )

    @admin.display(description='# expenses', ordering='num_of_expenses')
    def num_of_expenses(self, obj):
        url = (
                reverse('admin:expenses_expense_changelist')
                + '?'
                + urlencode({'grupe__id': obj.id})
        )
        return format_html('<a href="{}">{}</a>', url, obj.num_of_expenses)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', )
    list_select_related = ['user', ]
    actions = ['update_balance', ]

    @admin.action(description='Update balance')
    def update_balance(self, request, queryset):
        update_balance = queryset.update(balance=1000)
        self.message_user(
            request,
            f'{update_balance} updated balance to 1000',
            messages.SUCCESS,

        )
