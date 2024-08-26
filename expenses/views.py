from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import generic

from . import models
from . import forms


# Create your views here.
@login_required(login_url='login')
def profile_view(request):
    account = get_object_or_404(models.Account, user=request.user)
    return render(request, 'profile_detail.html', {'account': account})


@login_required()
def group_list_view(request):
    if request.method == 'POST':
        form = forms.GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group Created!')
    form = forms.GroupForm()
    groups = models.Group.objects.filter(members=request.user)
    context = {
        'groups': groups,
        'form': form,
    }
    return render(request, 'group_list_view.html', context)


@login_required()
def group_detail_view(request, pk):
    member_form = forms.AddMemberForm()
    group = get_object_or_404(models.Group.objects.prefetch_related('members'), pk=pk)
    group_members = group.members.all()
    expenses = models.Expense.objects.filter(grupe=group).select_related('grupe')
    if request.user not in group_members:
        messages.error(request, 'You are not allowed to view this group')
        return redirect('expenses:group-list')

    else:
        context = {
            'expenses': expenses,
            'group': group,
            'group_members': group_members,
            'member_form': member_form,
        }
        return render(request, 'group_detail_view.html', context)


class GroupUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Group
    form_class = forms.GroupUpdateForm
    template_name = 'grupe_update.html'

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        return reverse_lazy('expenses:group-detail', kwargs={'pk': pk})


@login_required()
def create_expense_view(request, pk):
    group = get_object_or_404(models.Group, pk=pk)

    if request.method == 'POST':
        form = forms.ExpensesForm(request.POST, group=group, current_user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.grupe = group
            expense.save()
            form.save_m2m()
            return redirect('expenses:group-detail', pk=group.id)
    else:
        form = forms.ExpensesForm(group=group, current_user=request.user, initial={
            'created_by': request.user,
            'grupe': group,
        })

    return render(request, 'expense_create_view.html', {'form': form})


@login_required()
def create_transactions_view(request, pk):
    current_user = request.user
    form = forms.TransactionForm()
    expenses = get_object_or_404(models.Expense.objects.select_related('grupe'), id=pk)
    participants = expenses.participants.all()
    share_per_person = round(expenses.amount / participants.count(), 2)
    payment_status = []

    for participant in participants:
        is_paid = models.Transaction.objects.filter(from_user=participant, expense=expenses).exists()
        payment_status.append((participant, is_paid))

    if request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            from_account = get_object_or_404(models.Account, user=transaction.from_user)
            to_account = get_object_or_404(models.Account, user=expenses.created_by)

            if from_account.balance >= share_per_person:
                from_account.balance -= share_per_person
                to_account.balance += share_per_person
                from_account.save()
                to_account.save()
                transaction.save()
                return redirect('expenses:group-detail', pk=expenses.grupe.id)
            else:
                form.add_error(None, f'Insufficient balance: Your account balance is {from_account.balance}.')
    is_paid = False
    in_participants = False
    is_creator = False
    if request.method == 'GET':
        if models.Transaction.objects.filter(from_user=current_user, expense=expenses).exists():
            is_paid = True
        if current_user not in list(participants):
            in_participants = True
        if request.user == expenses.created_by:
            is_creator = True
        form = forms.TransactionForm(initial={
            'from_user': current_user,
            'to_user': expenses.created_by,
            'amount': share_per_person,
            'expense': expenses,

        })

    return render(request, 'transaction_create.html', {
        'form': form,
        'share_per_person': share_per_person,
        'is_paid': is_paid,
        'is_creator': is_creator,
        'in_participants': in_participants,
        'participants': participants,
        'expenses': expenses,
        'payment_status': payment_status,
    })
