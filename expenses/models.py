from django.db import models
from django.conf import settings


# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=150)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='grupes')

    def __str__(self):
        return self.name


class Expense(models.Model):
    grupe = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='participants_expenses')

    def __str__(self):
        return f'{self.amount} {self.description}, {self.created_by.first_name}'


class Transaction(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='transactions')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gettransactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    datetime_created = models.DateTimeField(auto_now_add=True)


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

