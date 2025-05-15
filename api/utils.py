from django.utils.dateparse import parse_date
from django.http import JsonResponse

from datetime import timedelta
from django.utils import timezone
from mainapp.models import Transaction
from django.db.models import Sum

import logging

logger = logging.getLogger(__name__)

def filter_transactions_by_date(transactions, from_date_str, to_date_str, username):
    if from_date_str:
        from_date = parse_date(from_date_str)
        if from_date:
            transactions = transactions.filter(timestamp__date__gte=from_date)
        else:
            logger.error(f"User {username} provided invalid from_date: {from_date_str}")
            return None, JsonResponse({'errors': 'Некорректный формат from_date'}, status=400)
    if to_date_str:
        to_date = parse_date(to_date_str)
        if to_date:
            transactions = transactions.filter(timestamp__date__lte=to_date)
        else:
            logger.error(f"User {username} provided invalid to_date: {to_date_str}")
            return None, JsonResponse({'errors': 'Некорректный формат to_date'}, status=400)
    return transactions, None

def get_daily_and_weekly_spending(user):
    today = timezone.now().date()

    # Дневные траты
    daily_transactions = Transaction.objects.filter(user=user, timestamp__date=today)
    daily_spent = abs(sum(t.amount for t in daily_transactions))

    # Недельные траты
    week_start = today - timedelta(days=today.weekday())
    weekly_transactions = Transaction.objects.filter(
        user=user,
        timestamp__date__gte=week_start,
        timestamp__date__lte=today
    )
    weekly_spent = abs(sum(t.amount for t in weekly_transactions))

    return daily_spent, weekly_spent


def get_spending_by_category(transactions):
    by_category = {}
    for category, _ in Transaction.CATEGORY_CHOICES:
        category_sum = abs(
            transactions.filter(category=category).aggregate(total=Sum('amount'))['total'] or 0
        )
        if category_sum > 0:
            by_category[category] = float(category_sum)
    return by_category

