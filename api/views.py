from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from mainapp.forms import TransactionForm
from mainapp.models import UserProfile, Transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from django.db.models import Sum
from django.utils.dateparse import parse_date
import logging

from api.utils import get_daily_and_weekly_spending, filter_transactions_by_date, get_spending_by_category

logger = logging.getLogger(__name__)



@login_required
def create_transaction(request):
    if request.method != 'POST':
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)

    form = TransactionForm(request.POST)
    if not form.is_valid():
        logger.error(f"User {request.user.username} submitted invalid transaction form: {form.errors}")
        return JsonResponse({'errors': form.errors}, status=400)

    try:
        user_profile = request.user.userprofile
        amount = abs(form.cleaned_data['amount'])

        if amount > user_profile.balance:
            logger.warning(f"User {request.user.username} attempted transaction of {amount} with insufficient balance {user_profile.balance}")
            return JsonResponse({'errors': 'Недостаточно средств на балансе'}, status=400)

        daily_spent, weekly_spent = get_daily_and_weekly_spending(request.user)

        if daily_spent + amount > user_profile.daily_limit:
            logger.warning(f"User {request.user.username} exceeded daily limit: {daily_spent + amount} > {user_profile.daily_limit}")
            return JsonResponse({'errors': 'Превышен дневной лимит трат'}, status=400)

        if weekly_spent + amount > user_profile.weekly_limit:
            logger.warning(f"User {request.user.username} exceeded weekly limit: {weekly_spent + amount} > {user_profile.weekly_limit}")
            return JsonResponse({'errors': 'Превышен недельный лимит трат'}, status=400)

        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.amount = -amount
        transaction.save()

        user_profile.balance -= amount
        user_profile.save()

        logger.info(f"User {request.user.username} created transaction tx{transaction.id} for {amount}")
        return JsonResponse({
            "id": f"tx{transaction.id}",
            "user_id": transaction.user.id,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "category": transaction.category,
            "timestamp": transaction.timestamp.isoformat()
        })
    except Exception as e:
        logger.exception(f"Ошибка при создании транзакции: {e}")
        return JsonResponse({'errors': 'Внутренняя ошибка сервера'}, status=500)



@login_required
def get_user_stats(request):
    if request.method == 'GET':
        user_profile = request.user.userprofile
        today = timezone.now().date()

        daily_transactions = Transaction.objects.filter(
            user=request.user,
            timestamp__date=today
        )
        daily_spent = abs(sum(t.amount for t in daily_transactions))

        week_start = today - timedelta(days=today.weekday())
        weekly_transactions = Transaction.objects.filter(
            user=request.user,
            timestamp__date__gte=week_start,
            timestamp__date__lte=today
        )
        weekly_spent = abs(sum(t.amount for t in weekly_transactions))

        stats_data = {
            "balance": float(user_profile.balance),
            "daily_spent": float(daily_spent),
            "weekly_spent": float(weekly_spent)
        }
        logger.info(f"User {request.user.username} fetched user stats")
        return JsonResponse(stats_data)
    else:
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)


@login_required
def topup_balance(request):
    if request.method == 'POST':
        try:
            amount_str = request.POST.get('amount')
            if not amount_str:
                return JsonResponse({'errors': 'Сумма не указана'}, status=400)

            amount = Decimal(amount_str).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            if amount > 99999999.99 or amount < -99999999.99:
                return JsonResponse({'errors': 'Сумма превышает допустимый размер'}, status=400)

            user_profile = request.user.userprofile

            if user_profile.balance + amount < 0:
                logger.warning(f"User {request.user.username} attempted to withdraw {amount} with insufficient balance {user_profile.balance}")
                return JsonResponse({'errors': 'Недостаточно средств для списания'}, status=400)

            user_profile.balance += amount
            user_profile.save()

            logger.info(f"User {request.user.username} updated balance by {amount}, new balance: {user_profile.balance}")
            return JsonResponse({
                "message": "Баланс успешно обновлен",
                "balance": float(user_profile.balance)
            })
        except (InvalidOperation, ValueError, TypeError):
            logger.error(f"User {request.user.username} provided invalid amount: {amount_str}")
            return JsonResponse({'errors': 'Некорректная сумма'}, status=400)
    else:
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)


@login_required
def clear_transactions(request):
    if request.method == 'POST':
        try:
            Transaction.objects.filter(user=request.user).delete()
            logger.info(f"User {request.user.username} cleared all transactions")
            return JsonResponse({"message": "Все транзакции успешно удалены"})
        except Exception as e:
            logger.exception(f"Ошибка при удалении транзакций пользователя {request.user.username}: {e}")
            return JsonResponse({'errors': 'Не удалось удалить транзакции'}, status=500)
    else:
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)



@login_required
def spending_stats(request):
    if request.method != 'GET':
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)

    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    transactions = Transaction.objects.filter(user=request.user)

    transactions, error_response = filter_transactions_by_date(transactions, from_date, to_date, request.user.username)
    if error_response:
        return error_response

    total_spent = abs(transactions.aggregate(total=Sum('amount'))['total'] or 0)
    by_category = get_spending_by_category(transactions)
    unique_days = transactions.values('timestamp__date').distinct().count()
    daily_average = float(total_spent / unique_days) if unique_days > 0 else 0

    logger.info(f"User {request.user.username} fetched spending stats for period {from_date} to {to_date}")
    return JsonResponse({
        "total_spent": float(total_spent),
        "by_category": by_category,
        "daily_average": daily_average
    })


@login_required
def user_stats(request, id):
    if request.method != 'GET':
        return JsonResponse({'errors': 'Метод не разрешен'}, status=405)

    if id != request.user.id:
        logger.warning(f"User {request.user.username} attempted to access stats for user ID {id}")
        return JsonResponse({'errors': 'Доступ запрещен'}, status=403)

    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    transactions = Transaction.objects.filter(user=request.user)

    transactions, error_response = filter_transactions_by_date(transactions, from_date, to_date, request.user.username)
    if error_response:
        return error_response

    total_spent = abs(transactions.aggregate(total=Sum('amount'))['total'] or 0)
    by_category = get_spending_by_category(transactions)

    daily_data = transactions.values('timestamp__date').annotate(sum=Sum('amount')).order_by('timestamp__date')
    by_day = {
        entry['timestamp__date'].strftime('%Y-%m-%d'): float(abs(entry['sum']))
        for entry in daily_data
    }

    unique_days = transactions.values('timestamp__date').distinct().count()
    daily_average = float(total_spent / unique_days) if unique_days > 0 else 0

    logger.info(f"User {request.user.username} fetched stats for period {from_date} to {to_date}")
    return JsonResponse({
        "total_spent": float(total_spent),
        "by_category": by_category,
        "by_day": by_day,
        "daily_average": daily_average
    })