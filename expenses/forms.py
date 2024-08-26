from django import forms

from expenses.models import Group, Expense, Transaction


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'members': forms.CheckboxSelectMultiple(),
        }


class GroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'members']


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['members']


class ExpensesForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['grupe', 'description', 'created_by', 'amount', 'participants']
        widgets = {
            'grupe': forms.HiddenInput(),
            'created_by': forms.HiddenInput(),
            'participants': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['participants'].queryset = group.members.exclude(id=current_user.id)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['from_user', 'to_user', 'amount', 'expense']

        widgets = {
            'from_user': forms.HiddenInput(),
            'to_user': forms.HiddenInput(),
            'amount': forms.HiddenInput(),
            'expense': forms.HiddenInput(),
        }
