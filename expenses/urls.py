from django.urls import path
from django.conf.urls.i18n import i18n_patterns

from . import views

app_name = 'expenses'

urlpatterns = (
    path('', views.group_list_view, name='group-list'),
    path('profile/', views.profile_view, name='profile'),
    path('detail/<int:pk>/', views.group_detail_view, name='group-detail'),
    path('detail/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group-edit'),
    path('detail/<int:pk>/expenses/new/', views.create_expense_view, name='group-expense-new'),
    path('<int:pk>/transaction/', views.create_transactions_view, name='transaction-new'),

)
