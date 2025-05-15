from django.urls import path
from .views import create_transaction, get_user_stats, topup_balance, clear_transactions, spending_stats, user_stats

urlpatterns = [
    path('transactions/', create_transaction, name='create_transaction'),
    path('user-stats/', get_user_stats, name='get_user_stats'),
    path('topup/', topup_balance, name='topup_balance'),
    path('clear-transactions/', clear_transactions, name='clear_transactions'),
    path('spending-stats/', spending_stats, name='spending_stats'),
    path('users/<int:id>/stats/', user_stats, name='user_stats'),
]